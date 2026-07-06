                    /**
 * Автоматически сгенерированный заголовок протокола.
 * Не редактируйте вручную.
 */
#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <stdint.h>
#include <stdbool.h>

#define GETVERSION_CODE 0
#define GETSTATUS_CODE 1
#define RESET_CODE 2
#define GPIOINITOUTPUT_CODE 100
#define GPIOINITINPUT_CODE 101
#define GPIOSET_CODE 102
#define GPIOREAD_CODE 103
#define GPIODEINIT_CODE 104
#define ADCREAD_CODE 105
#define EEPROMREAD_CODE 106
#define I2CPROBE_CODE 107
#define I2CREADREGISTER_CODE 108
#define I2CWRITEREGISTER_CODE 109
#define I2CWRITE_CODE 110
#define I2CREAD_CODE 111
#define SPISEND_CODE 112
#define SPIRECEIVE_CODE 113
#define SPIEXCHANGE_CODE 114
#define UARTSEND_CODE 115
#define UARTRECEIVE_CODE 116
#define INITI2C_CODE 120
#define DEINITI2C_CODE 121
#define INITSPI_CODE 122
#define DEINITSPI_CODE 123
#define INITUART_CODE 124
#define DEINITUART_CODE 125
#define VERSIONINFORESPONSE_CODE 200
#define STATUSRESPONSE_CODE 201
#define GPIOREADRESPONSE_CODE 204
#define ADCREADRESPONSE_CODE 205
#define EEPROMREADRESPONSE_CODE 206
#define I2CPROBERESPONSE_CODE 207
#define I2CREADREGISTERRESPONSE_CODE 208
#define I2CREADRESPONSE_CODE 209
#define SPIRECEIVERESPONSE_CODE 210
#define SPIEXCHANGERESPONSE_CODE 211
#define UARTRECEIVERESPONSE_CODE 212
#define GENERICRESPONSE_CODE 250

/**
 * Запрос версии прошивки стенда
 * Код: 0
 */
typedef struct {
} RequestGetVersion;

/**
 * Запрос статуса (включено/выключено тестируемое устройство)
 * Код: 1
 */
typedef struct {
} RequestGetStatus;

/**
 * Перезагрузка стенда
 * Код: 2
 */
typedef struct {
} RequestReset;

/**
 * Инициализация пина как output
 * Код: 100
 */
typedef struct {
    uint8 pin;
    bool initial_state;
    bool open_drain;
} RequestGpioInitOutput;

/**
 * Инициализация пина как input
 * Код: 101
 */
typedef struct {
    uint8 pin;
    uint8 pull;
} RequestGpioInitInput;

/**
 * Установка состояния пина
 * Код: 102
 */
typedef struct {
    uint8 pin;
    bool value;
} RequestGpioSet;

/**
 * Чтение состояния пина
 * Код: 103
 */
typedef struct {
    uint8 pin;
} RequestGpioRead;

/**
 * Деинициализация пина (возврат в состояние по умолчанию)
 * Код: 104
 */
typedef struct {
    uint8 pin;
} RequestGpioDeinit;

/**
 * Чтение напряжения на канале АЦП
 * Код: 105
 */
typedef struct {
    uint8 channel;
} RequestAdcRead;

/**
 * Чтение данных из EEPROM оснастки
 * Код: 106
 */
typedef struct {
    uint16 address;
    uint8 len;
} RequestEepromRead;

/**
 * Проверка наличия устройства на шине I2C
 * Код: 107
 */
typedef struct {
    uint8 address;
} RequestI2cProbe;

/**
 * Чтение данных из регистра устройства I2C
 * Код: 108
 */
typedef struct {
    uint8 address;
    uint8 reg;
    uint8 len;
} RequestI2cReadRegister;

/**
 * Запись данных в регистр I2C
 * Код: 109
 */
typedef struct {
    uint8 address;
    uint8 reg;
    uint8 data_len;
    uint8_t data[8];
} RequestI2cWriteRegister;

/**
 * Отправка данных на устройство I2C без регистра
 * Код: 110
 */
typedef struct {
    uint8 address;
    uint8 data_len;
    uint8_t data[64];
} RequestI2cWrite;

/**
 * Чтение данных с устройства I2C
 * Код: 111
 */
typedef struct {
    uint8 address;
    uint8 len;
} RequestI2cRead;

/**
 * Отправка данных по SPI
 * Код: 112
 */
typedef struct {
    uint8 spi_num;
    uint8 data_len;
    uint8_t data[64];
} RequestSpiSend;

/**
 * Прием данных по SPI (с отправкой dummy байт)
 * Код: 113
 */
typedef struct {
    uint8 spi_num;
    uint8 len;
} RequestSpiReceive;

/**
 * Полнодуплексный обмен по SPI (отправка и прием одновременно)
 * Код: 114
 */
typedef struct {
    uint8 spi_num;
    uint8 tx_len;
    uint8_t tx_data[64];
} RequestSpiExchange;

/**
 * Отправка данных по UART
 * Код: 115
 */
typedef struct {
    uint8 uart_num;
    uint8 data_len;
    uint8_t data[64];
} RequestUartSend;

/**
 * Ожидание и прием данных по UART с таймаутом
 * Код: 116
 */
typedef struct {
    uint8 uart_num;
    uint16 timeout_ms;
    uint8 max_len;
} RequestUartReceive;

/**
 * Инициализация модуля I2C с указанием пинов
 * Код: 120
 */
typedef struct {
    uint8 i2c_num;
    uint8 scl_pin;
    uint8 sda_pin;
    uint32 speed;
} RequestInitI2c;

/**
 * Деинициализация модуля I2C
 * Код: 121
 */
typedef struct {
    uint8 i2c_num;
} RequestDeinitI2c;

/**
 * Инициализация модуля SPI
 * Код: 122
 */
typedef struct {
    uint8 spi_num;
    uint32 speed;
    uint8 mode;
    uint8 bit_order;
} RequestInitSpi;

/**
 * Деинициализация модуля SPI
 * Код: 123
 */
typedef struct {
    uint8 spi_num;
} RequestDeinitSpi;

/**
 * Инициализация модуля UART
 * Код: 124
 */
typedef struct {
    uint8 uart_num;
    uint32 baudrate;
    uint8 parity;
    uint8 stop_bits;
    uint8 data_bits;
} RequestInitUart;

/**
 * Деинициализация модуля UART
 * Код: 125
 */
typedef struct {
    uint8 uart_num;
} RequestDeinitUart;


/**
 * Ответ на GetVersion
 * Код: 200
 */
typedef struct {
    uint8 major;
    uint8 minor;
    uint8 patch;
} ResponseVersionInfoResponse;

/**
 * Ответ на GetStatus
 * Код: 201
 */
typedef struct {
    bool powered;
} ResponseStatusResponse;

/**
 * Ответ на GpioRead
 * Код: 204
 */
typedef struct {
    uint8 status;
    uint8 error_code;
    bool value;
} ResponseGpioReadResponse;

/**
 * Ответ на AdcRead
 * Код: 205
 */
typedef struct {
    uint8 status;
    uint8 error_code;
    uint16 voltage_mv;
} ResponseAdcReadResponse;

/**
 * Ответ на EepromRead
 * Код: 206
 */
typedef struct {
    uint8 status;
    uint8 error_code;
    uint8 data_len;
    uint8_t data[64];
} ResponseEepromReadResponse;

/**
 * Ответ на I2cProbe
 * Код: 207
 */
typedef struct {
    uint8 status;
    uint8 error_code;
    bool present;
} ResponseI2cProbeResponse;

/**
 * Ответ на I2cReadRegister
 * Код: 208
 */
typedef struct {
    uint8 status;
    uint8 error_code;
    uint8 data_len;
    uint8_t data[8];
} ResponseI2cReadRegisterResponse;

/**
 * Ответ на I2cRead
 * Код: 209
 */
typedef struct {
    uint8 status;
    uint8 error_code;
    uint8 data_len;
    uint8_t data[64];
} ResponseI2cReadResponse;

/**
 * Ответ на SpiReceive
 * Код: 210
 */
typedef struct {
    uint8 status;
    uint8 error_code;
    uint8 data_len;
    uint8_t data[64];
} ResponseSpiReceiveResponse;

/**
 * Ответ на SpiExchange
 * Код: 211
 */
typedef struct {
    uint8 status;
    uint8 error_code;
    uint8 rx_len;
    uint8_t rx_data[64];
} ResponseSpiExchangeResponse;

/**
 * Ответ на UartReceive
 * Код: 212
 */
typedef struct {
    uint8 status;
    uint8 error_code;
    uint8 data_len;
    uint8_t data[64];
} ResponseUartReceiveResponse;

/**
 * Общий ответ для команд без данных (инициализации, установка, запись и т.д.)
 * Код: 250
 */
typedef struct {
    uint8 status;
    uint8 error_code;
} ResponseGenericResponse;


// Функции сериализации/десериализации
uint8_t serialize_request(uint8_t cmd_code, const void* req, uint8_t* buf);
uint8_t deserialize_request(uint8_t cmd_code, const uint8_t* buf, void* req);
uint8_t serialize_response(uint8_t cmd_code, const void* resp, uint8_t* buf);
uint8_t deserialize_response(uint8_t cmd_code, const uint8_t* buf, void* resp);

#endif // PROTOCOL_H