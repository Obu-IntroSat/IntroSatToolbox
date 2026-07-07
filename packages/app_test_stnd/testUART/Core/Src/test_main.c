// test_main.c – версия для тестирования на хосте (без реального STM32)
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>   // для sleep (на Windows можно заменить на Sleep)
#include "protocol.h"

// ===== Эмуляция HAL (заглушки) =====
typedef struct { int dummy; } UART_HandleTypeDef;
UART_HandleTypeDef huart1;

void HAL_Init(void) {}
void HAL_Delay(uint32_t ms) {
    // Для Unix:
    // usleep(ms * 1000);
    // Для Windows: Sleep(ms);
}

int HAL_UART_Receive(UART_HandleTypeDef* huart, uint8_t* pData, uint16_t Size, uint32_t Timeout) {
    (void)huart;
    (void)Timeout;
    for (uint16_t i = 0; i < Size; i++) {
        int c = getchar();
        if (c == EOF) return -1;
        pData[i] = (uint8_t)c;
    }
    return 0;
}

int HAL_UART_Transmit(UART_HandleTypeDef* huart, const uint8_t* pData, uint16_t Size, uint32_t Timeout) {
    (void)huart;
    (void)Timeout;
    for (uint16_t i = 0; i < Size; i++) {
        putchar(pData[i]);
    }
    fflush(stdout);
    return 0;
}

void HAL_GPIO_WritePin(void* port, uint16_t pin, uint8_t state) {}
void MX_GPIO_Init(void) {}
void MX_USART1_UART_Init(void) {}
void SystemClock_Config(void) {}
void Error_Handler(void) { while(1); }

// ===== Основная логика (адаптирована под protocol.h) =====
#define START_BYTE 0xAA

static uint8_t calc_crc(const uint8_t* data, uint8_t len) {
    uint8_t crc = 0;
    for (uint8_t i = 0; i < len; i++) {
        crc ^= data[i];
    }
    return crc;
}

static void send_response(uint8_t cmd_code, const void* resp, uint8_t resp_len) {
    uint8_t data[64];
    uint8_t data_len = serialize_response(cmd_code, resp, data);
    if (data_len != resp_len) {
        // можно обработать ошибку, но игнорируем
    }

    uint8_t packet[64];
    uint8_t idx = 0;
    packet[idx++] = START_BYTE;
    packet[idx++] = cmd_code;
    packet[idx++] = data_len;
    memcpy(&packet[idx], data, data_len);
    idx += data_len;

    uint8_t crc = calc_crc(&packet[1], 2 + data_len);
    packet[idx++] = crc;

    HAL_UART_Transmit(&huart1, packet, idx, 300);
}

int main(void) {
    while (1) {
        uint8_t header[3];
        if (HAL_UART_Receive(&huart1, header, 3, 800) != 0) continue;
        if (header[0] != START_BYTE) continue;

        uint8_t cmd_code = header[1];
        uint8_t data_len = header[2];

        uint8_t data[64];
        if (data_len > 0) {
            if (data_len > sizeof(data)) continue;
            if (HAL_UART_Receive(&huart1, data, data_len, 200) != 0) continue;
        }

        uint8_t crc_received;
        if (HAL_UART_Receive(&huart1, &crc_received, 1, 200) != 0) continue;

        uint8_t crc_calc = calc_crc(&header[1], 2 + data_len);
        if (crc_calc != crc_received) continue;

        // --- Обработка команд ---
        if (cmd_code == GETVERSION_CODE) {
            ResponseVersionInfoResp resp = { .major = 0, .minor = 1, .patch = 0 };
            send_response(VERSIONINFORESP_CODE, &resp, sizeof(resp));
        }
        else if (cmd_code == GETSTATUS_CODE) {
            ResponseStatusResp resp = { .powered = false };
            send_response(STATUSRESP_CODE, &resp, sizeof(resp));
        }
        else {
            ResponseGenericResp resp = { .status = 1, .error_code = 100 };
            send_response(GENERICRESP_CODE, &resp, sizeof(resp));
        }

        HAL_Delay(30);
    }
    return 0;
}