/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "protocol.h"   // <-- добавлен сгенерированный протокол
#include <string.h>
#include <stdio.h>

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define START_BYTE 0xAA   // стартовый байт
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
UART_HandleTypeDef huart1;

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART1_UART_Init(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/**
  * @brief  Вычисляет XOR-контрольную сумму (CRC) для буфера данных.
  * @param  data: указатель на буфер
  * @param  len:  длина буфера в байтах
  * @retval вычисленное CRC (1 байт)
  */
static uint8_t calc_crc(const uint8_t* data, uint8_t len) {
    uint8_t crc = 0;
    for (uint8_t i = 0; i < len; i++) {
        crc ^= data[i];
    }
    return crc;
}

/**
  * @brief  Отправляет ответ на команду.
  * @param  cmd_code: код ответа (из protocol.h, например VERSIONINFORESP_CODE)
  * @param  resp:     указатель на структуру ответа (тип зависит от cmd_code)
  * @param  resp_len: размер данных ответа в байтах (возвращает serialize_response)
  */
static void send_response(uint8_t cmd_code, const void* resp, uint8_t resp_len) {
    uint8_t data[64];
    // Сериализуем структуру ответа в байтовый массив
    uint8_t data_len = serialize_response(cmd_code, resp, data);
    // Если длина не совпадает (на всякий случай), используем data_len
    if (data_len != resp_len) {
        // Можно добавить обработку ошибки, но игнорируем
    }

    // Формируем полный пакет: старт, код, длина, данные, CRC
    uint8_t packet[64];
    uint8_t idx = 0;
    packet[idx++] = START_BYTE;
    packet[idx++] = cmd_code;
    packet[idx++] = data_len;
    memcpy(&packet[idx], data, data_len);
    idx += data_len;

    // Вычисляем CRC по байтам: код, длина, данные (без стартового байта)
    uint8_t crc = calc_crc(&packet[1], 2 + data_len);
    packet[idx++] = crc;

    // Отправляем через UART
    HAL_UART_Transmit(&huart1, packet, idx, 300);
}

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USART1_UART_Init();
  /* USER CODE BEGIN 2 */

  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
      HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET); // LED выкл (мигает при приёме)

      uint8_t header[3];

      // Ждём заголовок (стартбайт, код, длина) с таймаутом 800 мс
      if (HAL_UART_Receive(&huart1, header, 3, 800) != HAL_OK) {
          continue; // таймаут – возвращаемся в начало цикла
      }

      // Проверяем стартовый байт
      if (header[0] != START_BYTE) {
          continue;
      }

      uint8_t cmd_code = header[1];   // код команды
      uint8_t data_len = header[2];   // длина данных

      // Буфер для данных
      uint8_t data[64];
      if (data_len > 0) {
          if (data_len > sizeof(data)) {
              continue; // слишком длинный пакет – игнорируем
          }
          if (HAL_UART_Receive(&huart1, data, data_len, 200) != HAL_OK) {
              continue;
          }
      }

      // Читаем байт CRC
      uint8_t crc_received;
      if (HAL_UART_Receive(&huart1, &crc_received, 1, 200) != HAL_OK) {
          continue;
      }

      // Проверяем CRC
      uint8_t crc_calc = calc_crc(&header[1], 2 + data_len); // header[1]=код, header[2]=длина
      if (crc_calc != crc_received) {
          // Ошибка CRC – игнорируем пакет
          continue;
      }

      // --- Пакет принят корректно. Обрабатываем команду ---

      if (cmd_code == GETVERSION_CODE) {
          // Запрос версии – формируем ответ
          ResponseVersionInfoResp resp = {
              .major = 0,
              .minor = 1,
              .patch = 0
          };
          send_response(VERSIONINFORESP_CODE, &resp, sizeof(resp));
      }
      else if (cmd_code == GETSTATUS_CODE) {
          // Запрос статуса – отвечаем: питание выключено (0)
          ResponseStatusResp resp = {
              .powered = false
          };
          send_response(STATUSRESP_CODE, &resp, sizeof(resp));
      }
      else {
          // Неизвестная команда – возвращаем ошибку
          ResponseGenericResp resp = {
              .status = 1,      // ERROR
              .error_code = 100 // код ошибки (можно задать любой)
          };
          send_response(GENERICRESP_CODE, &resp, sizeof(resp));
      }

      HAL_Delay(30); // небольшая задержка, чтобы не забивать UART
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief USART1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART1_UART_Init(void)
{
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 9600;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);

  GPIO_InitStruct.Pin = GPIO_PIN_13;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef USE_FULL_ASSERT
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */