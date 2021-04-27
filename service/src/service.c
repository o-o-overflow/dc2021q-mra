#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

// idea from https://isevenapi.xyz/

uint8_t unhex(char c)
{
    if (c >= '0' && c <= '9') {
        return c - '0';
    } else if (c >= 'a' && c <= 'f') {
        return c - 'a' + 10;
    } else if (c >= 'A' && c <= 'F') {
        return c - 'A' + 10;
    } else {
        return 0;
    }
}

int url_decode(char *dst, const char *src)
{
    for (int i = 0, j = 0; ; ) {
        char c = src[i];
        if (c == '\0') {
            return j;
        } else if (c == '%') {
            c = (unhex(src[i + 1]) << 4) | (unhex(src[i + 2]));
            i += 3;
        } else {
            i += 1;
        }
        dst[j++] = c;
    }
}

int response(int code, const char *info)
{
    if (code == 200) {
        printf("HTTP/1.1 200 OK\r\n");
    } else if (code == 401){
        printf("HTTP/1.1 401 Unauthorized\r\n");
    }
    printf("Content-Type: application/json\r\nContent-Length: %ld\r\n\r\n%s", strlen(info), info);
}

int main(int argc, char** argv) {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
    const char *path = "GET /api/isodd/";
    const char *ad = "Buy isOddCoin, the hottest new cryptocurrency!";
    char number[0x10] = {0};
    char buf[0x400] = {0};
    char *token = "public";
    int n = read(0, buf, sizeof(buf) - 1);
    if (n > sizeof(path) && strncmp(&buf[0], path, 15) == 0) {
        char *endl = strchr(buf, '\n');
        if (endl != NULL) {
            *endl = '\0';
            if (*--endl == '\r') {
                *endl = '\0';
            }
        }
        endl = strstr(buf, " HTTP/");
        if (endl != NULL) {
            *endl = '\0';
        }

        char *query = strchr(buf, '?');
        if (query != NULL) {
            *query = '\0';
            query++;
            if (!strncmp(query, "token=", 6)) {
                token = query + 6;
            }
        }
        char *request = &buf[15];
        char *slash = strchr(request, '/');
        if (slash != NULL) {
            *slash = '\0';
        }

        const char *resp = NULL;

        size_t n = strlen(request);
        if (!strcmp(token, "enterprise")) {
            if (n > 12) {
                response(401, "{\n\t\"error\": \"contact us for unlimited large number support\"\n}");
                return 0;
            }
        } else if (!strcmp(token, "premium")) {
            if (n > 9) {
                response(401, "{\n\t\"error\": \"sign up for enterprise to get large number support\"\n}");
                return 0;
            }
        } else {
            token = "public";
            if (n > 6) {
                response(401, "{\n\t\"error\": \"sign up for premium or enterprise to get large number support\"\n}");
                return 0;
            }
        }

        n = url_decode(number, request);
        // fprintf(stderr, "the number %s %d %d\n", number, strlen(number), n);

        if (number[0] == '-' && !strcmp(token, "public")) {
            response(401, "{\n\t\"error\": \"sign up for premium or enterprise to get negative number support\"\n}");
            return 0;
        } else {
            int last_digit = number[n - 1] - '0';
            char *msg = NULL;
            if (!strcmp(token, "public")) {
                asprintf(&msg, "{\n\t\"isodd\": %s,\n\t\"ad\": \"%s\"\n}\n", (last_digit % 2 == 1) ? "true": "false", ad);
            } else {
                asprintf(&msg, "{\n\t\"isodd\": %s\n}\n", (last_digit % 2 == 1) ? "true": "false");
            }
            response(200, msg);
            return 0;
        }
    }
    return 0;
}
