import sys, re

def _fix_init_fini(lines, start):
    assert lines[start + 2] == '\tstp x29,x30,[sp,-16]!\n'
    assert lines[start + 3] == '\tmov x29,sp\n'
    lines[start + 2] = '\tstp x29,x30,[sp,16]!\n'
    return True

def _fix_start_c(lines, start):
    assert lines[start + 1] == '_start_c:\n'
    lines[start + 1] += '\tsub sp, sp, #0x80000\n'
    return False

SKIPLIST = {
        # special functions
        '_start', '_longjmp', 'longjmp', 'sigsetjmp', '__sigsetjmp',
        }

ABORTLIST = {
        # large stack frame
        '__alt_socketcall', '__inet_aton', '__res_mkquery', 'child',
        }

FIXLIST = {
        '_init': _fix_init_fini,
        '_fini': _fix_init_fini,
        '_start_c': _fix_start_c,
        }

PAT0 = re.compile(r'\[sp, (-?\d+)\]!')
PAT0_FIX = re.compile(r'\[sp, -?\d+\]!')
PAT1 = re.compile(r'\[sp\], (\d+)')
PAT1_FIX = re.compile(r'\[sp\], \d+')

OP0 = {'str', 'ldr', 'strb', 'ldrb', 'ldrsw'}
OP1 = {'stp', 'ldp'}

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('usage: %s source generated' % sys.argv[0])
        sys.exit(-1)

    with open(sys.argv[1], 'r') as fin:
        lines = fin.readlines()

        # process functions
        i = 0
        while i < len(lines):
            if lines[i].find('%function') != -1:
                func = lines[i].split()[1].split(',')[0]
                print('processing function %s' % func)

                if func in FIXLIST:
                    if FIXLIST[func](lines, i):
                        i += 1
                        continue
                if func in SKIPLIST:
                    i += 1
                    continue
                elif func in ABORTLIST:
                    lines[i + 1] += '\n\tbrk #0\n'
                    i += 1
                    continue

                j = i + 1
                assert lines[j].startswith(func)
                use_stack = False
                x16 = 0
                startproc, endproc, stack_size = -1, -1, 0
                while j < len(lines):
                    if lines[j] == '\t.cfi_startproc\n':
                        assert startproc == -1, startproc
                        startproc = j
                        print('%s %d: start' % (func, startproc))
                        if j + 1 < len(lines) and lines[j + 1].startswith('\tmov\tx16'):
                            x16 = int(lines[j + 1].split()[-1].strip('\n'))
                    elif lines[j] == '\t.cfi_endproc\n':
                        assert endproc == -1, endproc
                        endproc = j
                        print('%s %d: end' % (func, endproc))
                        break
                    elif lines[j].startswith('\t.cfi_def_cfa_offset'):
                        def_cfa_offset = int(lines[j].split()[-1])
                        # print(lines[j - 1])
                        if def_cfa_offset != 0 and stack_size == 0:
                            stack_size = def_cfa_offset
                            print('%s stack size %#x' % (func, stack_size))
                    elif lines[j] == '\tret\n':
                        if startproc == -1 and endproc == -1:
                            print('%s don\'t use stack' % func)
                            assert not use_stack
                            break
                    elif not use_stack and lines[j].find('sp,') != -1:
                        use_stack = True

                    j += 1

                if not use_stack:
                    i = j
                    continue

                assert startproc != -1 and endproc != -1

                j = startproc
                while j < endproc:
                    # eliminate '!'
                    m = PAT0.findall(lines[j])
                    if len(m) > 0:
                        offset = int(m[0])
                        lines[j] = PAT0_FIX.sub('[sp]', lines[j])
                        lines.insert(j, '\tadd\tsp, sp, %d\n' % offset)
                        endproc += 1
                    m = PAT1.findall(lines[j])
                    if len(m) > 0:
                        offset = int(m[0])
                        lines[j] = PAT1_FIX.sub('[sp]', lines[j])
                        lines.insert(j + 1, '\tadd\tsp, sp, %d\n' % offset)
                        endproc += 1
                    j += 1

                j = startproc
                while j < endproc:
                    if lines[j].find('sp') != -1:
                        op = lines[j].replace(',', ', ').split()
                        new = None
                        if op[0] == 'sub':
                            if op[1] == op[2] == 'sp,':
                                new = lines[j].replace('sub', 'add')
                        elif op[0] == 'add':
                            if op[1] == op[2] == 'sp,':
                                new = lines[j].replace('add', 'sub')
                            elif op[2] == 'sp,':
                                offset = int(op[3])
                                # assert 0 <= offset < stack_size, lines[j]
                                assert (0 <= offset <= stack_size) or (offset % 0x100 == 0), lines[j]
                                offset -= stack_size
                                if -offset <= 0x1000:
                                    new = '\tsub\t%s sp, %d\n' % (op[1], -offset)
                                else:
                                    assert x16 != 0 and -offset - x16 < 0x1000
                                    new = '\tsub\tsp, sp, x16\n'
                                    new += '\tsub\t%s sp, %d\n' % (op[1], -offset - x16)
                                    new += '\tadd\tsp, sp, x16\n'
                        elif op[0] in OP0:
                            if op[2].startswith('[sp'):
                                if len(op) == 4:
                                    offset = int(op[3].strip(']'))
                                else:
                                    assert len(op) == 3
                                    offset = 0
                                assert 0 <= offset < stack_size, lines[j]
                                offset -= stack_size
                                if offset >= -0x100:
                                    new = '\t%s\t%s [sp, %d]\n' % (op[0], op[1], offset)
                                elif offset >= -0x1000:
                                    new = '\tsub\tsp, sp, %d\n' % (-offset)
                                    new += '\t%s\t%s [sp]\n' % (op[0], op[1])
                                    new += '\tadd\tsp, sp, %d\n' % (-offset)
                                else:
                                    assert x16 != 0 and -offset - x16 < 0x1000
                                    new = '\tsub\tsp, sp, x16\n'
                                    new += '\tsub\tsp, sp, %d\n' % (-offset - x16)
                                    new += '\t%s\t%s [sp]\n' % (op[0], op[1])
                                    new += '\tadd\tsp, sp, %d\n' % (-offset - x16)
                                    new += '\tadd\tsp, sp, x16\n'
                        elif op[0] in OP1:
                            if op[3].startswith('[sp'):
                                if len(op) == 5:
                                    offset = int(op[4].strip(']'))
                                else:
                                    assert len(op) == 4
                                    offset = 0
                                assert 0 <= offset < stack_size, lines[j]
                                offset -= stack_size
                                if offset >= -0x100:
                                    new = '\t%s\t%s %s [sp, %d]\n' % (op[0], op[1], op[2], offset)
                                elif offset >= -0x1000:
                                    new = '\tsub\tsp, sp, %d\n' % (-offset)
                                    new += '\t%s\t%s %s [sp]\n' % (op[0], op[1], op[2])
                                    new += '\tadd\tsp, sp, %d\n' % (-offset)
                                else:
                                    assert x16 != 0 and -offset - x16 < 0x1000
                                    new = '\tsub\tsp, sp, x16\n'
                                    new += '\tsub\tsp, sp, %d\n' % (-offset - x16)
                                    new += '\t%s\t%s %s [sp]\n' % (op[0], op[1], op[2])
                                    new += '\tadd\tsp, sp, %d\n' % (-offset - x16)
                                    new += '\tadd\tsp, sp, x16\n'

                        if new is not None:
                            assert lines[j] != new
                            lines[j] = new
                        else:
                            print('skip %s' % ' '.join(op))

                    j += 1

                i = j

            i += 1

    with open(sys.argv[2], 'w') as fout:
        fout.write(''.join(lines))
