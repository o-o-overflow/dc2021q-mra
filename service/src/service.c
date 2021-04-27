#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

// idea from https://isevenapi.xyz/

int main(int argc, char** argv) {
    const char *path = "GET /api/isodd/";
    const char *ad = "Buy isOddCoin, the hottest new cryptocurrency!";
    char number[0x20] = {0};
    char buf[0x400] = {0};
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

        char *token = "public";
        char *query = strchr(buf, '?');
        if (query != NULL) {
            *query = '\0';
            query++;
            if (!strncmp(query, "token=", 6)) {
                token = query + 6;
            }
        }
        const char *request = &buf[15];
        char *slash = strchr(request, '/');
        if (slash != NULL) {
            *slash = '\0';
        }

        size_t n = strlen(request);
        if (!strcmp(token, "enterprise")) {
        } else if (!strcmp(token, "premium")) {
            if (n > 9) {
                puts("{\n\t\"error\": \"sign up for enterprise to get large number support\"\n}");
                return 0;
            }
        } else {
            token = "public";
            if (n > 6) {
                puts("{\n\t\"error\": \"sign up for premium or enterprise to get large number support\"\n}");
                return 0;
            }
        }
        memcpy(&number, request, n);
        number[n] = 0;

        if (number[0] == '-' && !strcmp(token, "public")) {
            puts("{\n\t\"error\": \"sign up for premium or enterprise to get negative number support\"\n}");
            return 0;
        } else {
            int last_digit = number[n - 1] - '0';
            if (!strcmp(token, "public")) {
                printf("{\n\t\"isodd\": %s,\n\t\"ad\": \"%s\"\n}", (last_digit % 2 == 1) ? "true": "false", ad);
            } else {
                printf("{\n\t\"isodd\": %s\n}", (last_digit % 2 == 1) ? "true": "false");
            }
            return 0;
        }
    }
    return 0;
}
