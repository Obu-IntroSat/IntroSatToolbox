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
#define VERSIONINFORESP_CODE 200
#define STATUSRESP_CODE 201
#define GPIOREADRESP_CODE 204
#define ADCREADRESP_CODE 205
#define EEPROMREADRESP_CODE 206
#define I2CPROBERESP_CODE 207
#define I2CREADREGISTERRESP_CODE 208
#define I2CREADRESP_CODE 209
#define SPIRECEIVERESP_CODE 210
#define SPIEXCHANGERESP_CODE 211
#define UARTRECEIVERESP_CODE 212
#define GENERICRESP_CODE 250

// ---------- Коды ошибок ----------
#define WRONG_OPCODE 100
#define UART_INIT_FAIL 200
#define UART_INVALID_NUM 210
#define UART_INVALID_STOP_BITS 220
#define UART_INVALID_PARITY 230
#define UART_INVALID_DATA_BITS 240

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
    uint8_t pin;
    bool initial_state;
    bool open_drain;
} RequestGpioInitOutput;

/**
 * Инициализация пина как input
 * Код: 101
 */
typedef struct {
    uint8_t pin;
    uint8_t pull;
} RequestGpioInitInput;

/**
 * Установка состояния пина
 * Код: 102
 */
typedef struct {
    uint8_t pin;
    bool value;
} RequestGpioSet;

/**
 * Чтение состояния пина
 * Код: 103
 */
typedef struct {
    uint8_t pin;
} RequestGpioRead;

/**
 * Деинициализация пина (возврат в состояние по умолчанию)
 * Код: 104
 */
typedef struct {
    uint8_t pin;
} RequestGpioDeinit;

/**
 * Чтение напряжения на канале АЦП
 * Код: 105
 */
typedef struct {
    uint8_t channel;
} RequestAdcRead;

/**
 * Чтение данных из EEPROM оснастки
 * Код: 106
 */
typedef struct {
    uint16_t address;
    uint8_t len;
} RequestEepromRead;

/**
 * Проверка наличия устройства на шине I2C
 * Код: 107
 */
typedef struct {
    uint8_t i2c_interface;
    uint16_t address;
} RequestI2cProbe;

/**
 * Чтение данных из регистра устройства I2C
 * Код: 108
 */
typedef struct {
    uint8_t i2c_interface;
    uint16_t address;
    uint8_t reg;
    uint8_t len;
} RequestI2cReadRegister;

/**
 * Запись данных в регистр I2C
 * Код: 109
 */
typedef struct {
    uint8_t i2c_interface;
    uint16_t address;
    uint8_t reg;
    uint8_t data_len;
    uint8_t data[8];
} RequestI2cWriteRegister;

/**
 * Отправка данных на устройство I2C без регистра
 * Код: 110
 */
typedef struct {
    uint8_t i2c_interface;
    uint16_t address;
    uint8_t data_len;
    uint8_t data[64];
} RequestI2cWrite;

/**
 * Чтение данных с устройства I2C
 * Код: 111
 */
typedef struct {
    uint8_t i2c_interface;
    uint16_t address;
    uint8_t len;
} RequestI2cRead;

/**
 * Отправка данных по SPI
 * Код: 112
 */
typedef struct {
    uint8_t spi_num;
    uint8_t data_len;
    uint8_t data[64];
} RequestSpiSend;

/**
 * Прием данных по SPI (с отправкой dummy байт)
 * Код: 113
 */
typedef struct {
    uint8_t spi_num;
    uint8_t len;
} RequestSpiReceive;

/**
 * Полнодуплексный обмен по SPI (отправка и прием одновременно)
 * Код: 114
 */
typedef struct {
    uint8_t spi_num;
    uint8_t tx_len;
    uint8_t tx_data[64];
} RequestSpiExchange;

/**
 * Отправка данных по UART
 * Код: 115
 */
typedef struct {
    uint8_t uart_num;
    uint8_t data_len;
    uint8_t data[64];
} RequestUartSend;

/**
 * Ожидание и прием данных по UART с таймаутом
 * Код: 116
 */
typedef struct {
    uint8_t uart_num;
    uint16_t timeout_ms;
    uint8_t max_len;
} RequestUartReceive;

/**
 * Инициализация модуля I2C с выбором интерфейса и режима адресации
 * Код: 120
 */
typedef struct {
    uint8_t i2c_interface;
    uint32_t speed;
    uint8_t addressing_mode;
} RequestInitI2c;

/**
 * Деинициализация модуля I2C
 * Код: 121
 */
typedef struct {
    uint8_t i2c_interface;
} RequestDeinitI2c;

/**
 * Инициализация модуля SPI
 * Код: 122
 */
typedef struct {
    uint8_t spi_num;
    uint32_t speed;
    uint8_t mode;
    uint8_t bit_order;
} RequestInitSpi;

/**
 * Деинициализация модуля SPI
 * Код: 123
 */
typedef struct {
    uint8_t spi_num;
} RequestDeinitSpi;

/**
 * Инициализация модуля UART
 * Код: 124
 */
typedef struct {
    uint8_t uart_num;
    uint32_t baudrate;
    uint8_t parity;
    uint8_t stop_bits;
    uint8_t data_bits;
} RequestInitUart;

/**
 * Деинициализация модуля UART
 * Код: 125
 */
typedef struct {
    uint8_t uart_num;
} RequestDeinitUart;


/**
 * Ответ на GetVersion
 * Код: 200
 */
typedef struct {
    uint8_t major;
    uint8_t minor;
    uint8_t patch;
} ResponseVersionInfoResp;

/**
 * Ответ на GetStatus
 * Код: 201
 */
typedef struct {
    bool powered;
} ResponseStatusResp;

/**
 * Ответ на GpioRead
 * Код: 204
 */
typedef struct {
    uint8_t status;
    uint8_t error_code;
    bool value;
} ResponseGpioReadResp;

/**
 * Ответ на AdcRead
 * Код: 205
 */
typedef struct {
    uint8_t status;
    uint8_t error_code;
    uint16_t voltage_mv;
} ResponseAdcReadResp;

/**
 * Ответ на EepromRead
 * Код: 206
 */
typedef struct {
    uint8_t status;
    uint8_t error_code;
    uint8_t data_len;
    uint8_t data[64];
} ResponseEepromReadResp;

/**
 * Ответ на I2cProbe
 * Код: 207
 */
typedef struct {
    uint8_t status;
    uint8_t error_code;
    bool present;
} ResponseI2cProbeResp;

/**
 * Ответ на I2cReadRegister
 * Код: 208
 */
typedef struct {
    uint8_t status;
    uint8_t error_code;
    uint8_t data_len;
    uint8_t data[8];
} ResponseI2cReadRegisterResp;

/**
 * Ответ на I2cRead
 * Код: 209
 */
typedef struct {
    uint8_t status;
    uint8_t error_code;
    uint8_t data_len;
    uint8_t data[64];
} ResponseI2cReadResp;

/**
 * Ответ на SpiReceive
 * Код: 210
 */
typedef struct {
    uint8_t status;
    uint8_t error_code;
    uint8_t data_len;
    uint8_t data[64];
} ResponseSpiReceiveResp;

/**
 * Ответ на SpiExchange
 * Код: 211
 */
typedef struct {
    uint8_t status;
    uint8_t error_code;
    uint8_t rx_len;
    uint8_t rx_data[64];
} ResponseSpiExchangeResp;

/**
 * Ответ на UartReceive
 * Код: 212
 */
typedef struct {
    uint8_t status;
    uint8_t error_code;
    uint8_t data_len;
    uint8_t data[64];
} ResponseUartReceiveResp;

/**
 * Общий ответ для команд без данных (инициализации, установка, запись и т.д.)
 * Код: 250
 */
typedef struct {
    uint8_t status;
    uint8_t error_code;
} ResponseGenericResp;


// Специализированные функции сериализации/десериализации
uint8_t serialize_RequestGetVersion(const RequestGetVersion* req, uint8_t* buf);
void deserialize_RequestGetVersion(const uint8_t* buf, RequestGetVersion* req);
uint8_t serialize_RequestGetStatus(const RequestGetStatus* req, uint8_t* buf);
void deserialize_RequestGetStatus(const uint8_t* buf, RequestGetStatus* req);
uint8_t serialize_RequestReset(const RequestReset* req, uint8_t* buf);
void deserialize_RequestReset(const uint8_t* buf, RequestReset* req);
uint8_t serialize_RequestGpioInitOutput(const RequestGpioInitOutput* req, uint8_t* buf);
void deserialize_RequestGpioInitOutput(const uint8_t* buf, RequestGpioInitOutput* req);
uint8_t serialize_RequestGpioInitInput(const RequestGpioInitInput* req, uint8_t* buf);
void deserialize_RequestGpioInitInput(const uint8_t* buf, RequestGpioInitInput* req);
uint8_t serialize_RequestGpioSet(const RequestGpioSet* req, uint8_t* buf);
void deserialize_RequestGpioSet(const uint8_t* buf, RequestGpioSet* req);
uint8_t serialize_RequestGpioRead(const RequestGpioRead* req, uint8_t* buf);
void deserialize_RequestGpioRead(const uint8_t* buf, RequestGpioRead* req);
uint8_t serialize_RequestGpioDeinit(const RequestGpioDeinit* req, uint8_t* buf);
void deserialize_RequestGpioDeinit(const uint8_t* buf, RequestGpioDeinit* req);
uint8_t serialize_RequestAdcRead(const RequestAdcRead* req, uint8_t* buf);
void deserialize_RequestAdcRead(const uint8_t* buf, RequestAdcRead* req);
uint8_t serialize_RequestEepromRead(const RequestEepromRead* req, uint8_t* buf);
void deserialize_RequestEepromRead(const uint8_t* buf, RequestEepromRead* req);
uint8_t serialize_RequestI2cProbe(const RequestI2cProbe* req, uint8_t* buf);
void deserialize_RequestI2cProbe(const uint8_t* buf, RequestI2cProbe* req);
uint8_t serialize_RequestI2cReadRegister(const RequestI2cReadRegister* req, uint8_t* buf);
void deserialize_RequestI2cReadRegister(const uint8_t* buf, RequestI2cReadRegister* req);
uint8_t serialize_RequestI2cWriteRegister(const RequestI2cWriteRegister* req, uint8_t* buf);
void deserialize_RequestI2cWriteRegister(const uint8_t* buf, RequestI2cWriteRegister* req);
uint8_t serialize_RequestI2cWrite(const RequestI2cWrite* req, uint8_t* buf);
void deserialize_RequestI2cWrite(const uint8_t* buf, RequestI2cWrite* req);
uint8_t serialize_RequestI2cRead(const RequestI2cRead* req, uint8_t* buf);
void deserialize_RequestI2cRead(const uint8_t* buf, RequestI2cRead* req);
uint8_t serialize_RequestSpiSend(const RequestSpiSend* req, uint8_t* buf);
void deserialize_RequestSpiSend(const uint8_t* buf, RequestSpiSend* req);
uint8_t serialize_RequestSpiReceive(const RequestSpiReceive* req, uint8_t* buf);
void deserialize_RequestSpiReceive(const uint8_t* buf, RequestSpiReceive* req);
uint8_t serialize_RequestSpiExchange(const RequestSpiExchange* req, uint8_t* buf);
void deserialize_RequestSpiExchange(const uint8_t* buf, RequestSpiExchange* req);
uint8_t serialize_RequestUartSend(const RequestUartSend* req, uint8_t* buf);
void deserialize_RequestUartSend(const uint8_t* buf, RequestUartSend* req);
uint8_t serialize_RequestUartReceive(const RequestUartReceive* req, uint8_t* buf);
void deserialize_RequestUartReceive(const uint8_t* buf, RequestUartReceive* req);
uint8_t serialize_RequestInitI2c(const RequestInitI2c* req, uint8_t* buf);
void deserialize_RequestInitI2c(const uint8_t* buf, RequestInitI2c* req);
uint8_t serialize_RequestDeinitI2c(const RequestDeinitI2c* req, uint8_t* buf);
void deserialize_RequestDeinitI2c(const uint8_t* buf, RequestDeinitI2c* req);
uint8_t serialize_RequestInitSpi(const RequestInitSpi* req, uint8_t* buf);
void deserialize_RequestInitSpi(const uint8_t* buf, RequestInitSpi* req);
uint8_t serialize_RequestDeinitSpi(const RequestDeinitSpi* req, uint8_t* buf);
void deserialize_RequestDeinitSpi(const uint8_t* buf, RequestDeinitSpi* req);
uint8_t serialize_RequestInitUart(const RequestInitUart* req, uint8_t* buf);
void deserialize_RequestInitUart(const uint8_t* buf, RequestInitUart* req);
uint8_t serialize_RequestDeinitUart(const RequestDeinitUart* req, uint8_t* buf);
void deserialize_RequestDeinitUart(const uint8_t* buf, RequestDeinitUart* req);

uint8_t serialize_ResponseVersionInfoResp(const ResponseVersionInfoResp* resp, uint8_t* buf);
void deserialize_ResponseVersionInfoResp(const uint8_t* buf, ResponseVersionInfoResp* resp);
uint8_t serialize_ResponseStatusResp(const ResponseStatusResp* resp, uint8_t* buf);
void deserialize_ResponseStatusResp(const uint8_t* buf, ResponseStatusResp* resp);
uint8_t serialize_ResponseGpioReadResp(const ResponseGpioReadResp* resp, uint8_t* buf);
void deserialize_ResponseGpioReadResp(const uint8_t* buf, ResponseGpioReadResp* resp);
uint8_t serialize_ResponseAdcReadResp(const ResponseAdcReadResp* resp, uint8_t* buf);
void deserialize_ResponseAdcReadResp(const uint8_t* buf, ResponseAdcReadResp* resp);
uint8_t serialize_ResponseEepromReadResp(const ResponseEepromReadResp* resp, uint8_t* buf);
void deserialize_ResponseEepromReadResp(const uint8_t* buf, ResponseEepromReadResp* resp);
uint8_t serialize_ResponseI2cProbeResp(const ResponseI2cProbeResp* resp, uint8_t* buf);
void deserialize_ResponseI2cProbeResp(const uint8_t* buf, ResponseI2cProbeResp* resp);
uint8_t serialize_ResponseI2cReadRegisterResp(const ResponseI2cReadRegisterResp* resp, uint8_t* buf);
void deserialize_ResponseI2cReadRegisterResp(const uint8_t* buf, ResponseI2cReadRegisterResp* resp);
uint8_t serialize_ResponseI2cReadResp(const ResponseI2cReadResp* resp, uint8_t* buf);
void deserialize_ResponseI2cReadResp(const uint8_t* buf, ResponseI2cReadResp* resp);
uint8_t serialize_ResponseSpiReceiveResp(const ResponseSpiReceiveResp* resp, uint8_t* buf);
void deserialize_ResponseSpiReceiveResp(const uint8_t* buf, ResponseSpiReceiveResp* resp);
uint8_t serialize_ResponseSpiExchangeResp(const ResponseSpiExchangeResp* resp, uint8_t* buf);
void deserialize_ResponseSpiExchangeResp(const uint8_t* buf, ResponseSpiExchangeResp* resp);
uint8_t serialize_ResponseUartReceiveResp(const ResponseUartReceiveResp* resp, uint8_t* buf);
void deserialize_ResponseUartReceiveResp(const uint8_t* buf, ResponseUartReceiveResp* resp);
uint8_t serialize_ResponseGenericResp(const ResponseGenericResp* resp, uint8_t* buf);
void deserialize_ResponseGenericResp(const uint8_t* buf, ResponseGenericResp* resp);

// Общие функции по коду команды
uint8_t serialize_request(uint8_t cmd_code, const void* req, uint8_t* buf);
void deserialize_request(uint8_t cmd_code, const uint8_t* buf, void* req);
uint8_t serialize_response(uint8_t cmd_code, const void* resp, uint8_t* buf);
void deserialize_response(uint8_t cmd_code, const uint8_t* buf, void* resp);

#endif // PROTOCOL_H