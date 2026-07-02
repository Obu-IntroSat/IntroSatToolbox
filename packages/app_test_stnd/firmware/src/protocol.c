/**
 * Автоматически сгенерированная реализация протокола.
 */
#include "protocol.h"
#include <string.h>

// Вспомогательная функция для копирования с учётом размера
static inline void pack_uint8(uint8_t val, uint8_t* buf) { *buf = val; }
static inline void pack_uint16(uint16_t val, uint8_t* buf) { memcpy(buf, &val, 2); }
static inline void pack_uint32(uint32_t val, uint8_t* buf) { memcpy(buf, &val, 4); }
static inline void pack_bool(bool val, uint8_t* buf) { *buf = val ? 1 : 0; }

static inline uint8_t unpack_uint8(const uint8_t* buf) { return *buf; }
static inline uint16_t unpack_uint16(const uint8_t* buf) { uint16_t v; memcpy(&v, buf, 2); return v; }
static inline uint32_t unpack_uint32(const uint8_t* buf) { uint32_t v; memcpy(&v, buf, 4); return v; }
static inline bool unpack_bool(const uint8_t* buf) { return *buf != 0; }

// Сериализация запроса
uint8_t serialize_request(uint8_t cmd_code, const void* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    switch (cmd_code) {
    case GETVERSION_CODE: {
        const RequestGetVersion* r = (const RequestGetVersion*)req;
        break;
    }
    case GETSTATUS_CODE: {
        const RequestGetStatus* r = (const RequestGetStatus*)req;
        break;
    }
    case RESET_CODE: {
        const RequestReset* r = (const RequestReset*)req;
        break;
    }
    case GPIOINITOUTPUT_CODE: {
        const RequestGpioInitOutput* r = (const RequestGpioInitOutput*)req;
        // Для простых типов
        pack_uint8(r->pin, ptr);
        ptr += sizeof(r->pin);
        // Для простых типов
        pack_bool(r->initial_state, ptr);
        ptr += sizeof(r->initial_state);
        // Для простых типов
        pack_bool(r->open_drain, ptr);
        ptr += sizeof(r->open_drain);
        break;
    }
    case GPIOINITINPUT_CODE: {
        const RequestGpioInitInput* r = (const RequestGpioInitInput*)req;
        // Для простых типов
        pack_uint8(r->pin, ptr);
        ptr += sizeof(r->pin);
        // Для простых типов
        pack_uint8(r->pull, ptr);
        ptr += sizeof(r->pull);
        break;
    }
    case GPIOSET_CODE: {
        const RequestGpioSet* r = (const RequestGpioSet*)req;
        // Для простых типов
        pack_uint8(r->pin, ptr);
        ptr += sizeof(r->pin);
        // Для простых типов
        pack_bool(r->value, ptr);
        ptr += sizeof(r->value);
        break;
    }
    case GPIOREAD_CODE: {
        const RequestGpioRead* r = (const RequestGpioRead*)req;
        // Для простых типов
        pack_uint8(r->pin, ptr);
        ptr += sizeof(r->pin);
        break;
    }
    case GPIODEINIT_CODE: {
        const RequestGpioDeinit* r = (const RequestGpioDeinit*)req;
        // Для простых типов
        pack_uint8(r->pin, ptr);
        ptr += sizeof(r->pin);
        break;
    }
    case ADCREAD_CODE: {
        const RequestAdcRead* r = (const RequestAdcRead*)req;
        // Для простых типов
        pack_uint8(r->channel, ptr);
        ptr += sizeof(r->channel);
        break;
    }
    case EEPROMREAD_CODE: {
        const RequestEepromRead* r = (const RequestEepromRead*)req;
        // Для простых типов
        pack_uint16(r->address, ptr);
        ptr += sizeof(r->address);
        // Для простых типов
        pack_uint8(r->len, ptr);
        ptr += sizeof(r->len);
        break;
    }
    case I2CPROBE_CODE: {
        const RequestI2cProbe* r = (const RequestI2cProbe*)req;
        // Для простых типов
        pack_uint8(r->address, ptr);
        ptr += sizeof(r->address);
        break;
    }
    case I2CREADREGISTER_CODE: {
        const RequestI2cReadRegister* r = (const RequestI2cReadRegister*)req;
        // Для простых типов
        pack_uint8(r->address, ptr);
        ptr += sizeof(r->address);
        // Для простых типов
        pack_uint8(r->reg, ptr);
        ptr += sizeof(r->reg);
        // Для простых типов
        pack_uint8(r->len, ptr);
        ptr += sizeof(r->len);
        break;
    }
    case I2CWRITEREGISTER_CODE: {
        const RequestI2cWriteRegister* r = (const RequestI2cWriteRegister*)req;
        // Для простых типов
        pack_uint8(r->address, ptr);
        ptr += sizeof(r->address);
        // Для простых типов
        pack_uint8(r->reg, ptr);
        ptr += sizeof(r->reg);
        // Для простых типов
        pack_uint8(r->data_len, ptr);
        ptr += sizeof(r->data_len);
        memcpy(ptr, r->data, sizeof(r->data));
        ptr += sizeof(r->data);
        break;
    }
    case I2CWRITE_CODE: {
        const RequestI2cWrite* r = (const RequestI2cWrite*)req;
        // Для простых типов
        pack_uint8(r->address, ptr);
        ptr += sizeof(r->address);
        // Для простых типов
        pack_uint8(r->data_len, ptr);
        ptr += sizeof(r->data_len);
        memcpy(ptr, r->data, sizeof(r->data));
        ptr += sizeof(r->data);
        break;
    }
    case I2CREAD_CODE: {
        const RequestI2cRead* r = (const RequestI2cRead*)req;
        // Для простых типов
        pack_uint8(r->address, ptr);
        ptr += sizeof(r->address);
        // Для простых типов
        pack_uint8(r->len, ptr);
        ptr += sizeof(r->len);
        break;
    }
    case SPISEND_CODE: {
        const RequestSpiSend* r = (const RequestSpiSend*)req;
        // Для простых типов
        pack_uint8(r->spi_num, ptr);
        ptr += sizeof(r->spi_num);
        // Для простых типов
        pack_uint8(r->data_len, ptr);
        ptr += sizeof(r->data_len);
        memcpy(ptr, r->data, sizeof(r->data));
        ptr += sizeof(r->data);
        break;
    }
    case SPIRECEIVE_CODE: {
        const RequestSpiReceive* r = (const RequestSpiReceive*)req;
        // Для простых типов
        pack_uint8(r->spi_num, ptr);
        ptr += sizeof(r->spi_num);
        // Для простых типов
        pack_uint8(r->len, ptr);
        ptr += sizeof(r->len);
        break;
    }
    case SPIEXCHANGE_CODE: {
        const RequestSpiExchange* r = (const RequestSpiExchange*)req;
        // Для простых типов
        pack_uint8(r->spi_num, ptr);
        ptr += sizeof(r->spi_num);
        // Для простых типов
        pack_uint8(r->tx_len, ptr);
        ptr += sizeof(r->tx_len);
        memcpy(ptr, r->tx_data, sizeof(r->tx_data));
        ptr += sizeof(r->tx_data);
        break;
    }
    case UARTSEND_CODE: {
        const RequestUartSend* r = (const RequestUartSend*)req;
        // Для простых типов
        pack_uint8(r->uart_num, ptr);
        ptr += sizeof(r->uart_num);
        // Для простых типов
        pack_uint8(r->data_len, ptr);
        ptr += sizeof(r->data_len);
        memcpy(ptr, r->data, sizeof(r->data));
        ptr += sizeof(r->data);
        break;
    }
    case UARTRECEIVE_CODE: {
        const RequestUartReceive* r = (const RequestUartReceive*)req;
        // Для простых типов
        pack_uint8(r->uart_num, ptr);
        ptr += sizeof(r->uart_num);
        // Для простых типов
        pack_uint16(r->timeout_ms, ptr);
        ptr += sizeof(r->timeout_ms);
        // Для простых типов
        pack_uint8(r->max_len, ptr);
        ptr += sizeof(r->max_len);
        break;
    }
    case INITI2C_CODE: {
        const RequestInitI2c* r = (const RequestInitI2c*)req;
        // Для простых типов
        pack_uint8(r->i2c_num, ptr);
        ptr += sizeof(r->i2c_num);
        // Для простых типов
        pack_uint32(r->speed, ptr);
        ptr += sizeof(r->speed);
        break;
    }
    case DEINITI2C_CODE: {
        const RequestDeinitI2c* r = (const RequestDeinitI2c*)req;
        // Для простых типов
        pack_uint8(r->i2c_num, ptr);
        ptr += sizeof(r->i2c_num);
        break;
    }
    case INITSPI_CODE: {
        const RequestInitSpi* r = (const RequestInitSpi*)req;
        // Для простых типов
        pack_uint8(r->spi_num, ptr);
        ptr += sizeof(r->spi_num);
        // Для простых типов
        pack_uint32(r->speed, ptr);
        ptr += sizeof(r->speed);
        // Для простых типов
        pack_uint8(r->mode, ptr);
        ptr += sizeof(r->mode);
        // Для простых типов
        pack_uint8(r->bit_order, ptr);
        ptr += sizeof(r->bit_order);
        break;
    }
    case DEINITSPI_CODE: {
        const RequestDeinitSpi* r = (const RequestDeinitSpi*)req;
        // Для простых типов
        pack_uint8(r->spi_num, ptr);
        ptr += sizeof(r->spi_num);
        break;
    }
    case INITUART_CODE: {
        const RequestInitUart* r = (const RequestInitUart*)req;
        // Для простых типов
        pack_uint8(r->uart_num, ptr);
        ptr += sizeof(r->uart_num);
        // Для простых типов
        pack_uint32(r->baudrate, ptr);
        ptr += sizeof(r->baudrate);
        // Для простых типов
        pack_uint8(r->parity, ptr);
        ptr += sizeof(r->parity);
        // Для простых типов
        pack_uint8(r->stop_bits, ptr);
        ptr += sizeof(r->stop_bits);
        // Для простых типов
        pack_uint8(r->data_bits, ptr);
        ptr += sizeof(r->data_bits);
        break;
    }
    case DEINITUART_CODE: {
        const RequestDeinitUart* r = (const RequestDeinitUart*)req;
        // Для простых типов
        pack_uint8(r->uart_num, ptr);
        ptr += sizeof(r->uart_num);
        break;
    }
    default:
        return 0; // неизвестная команда
    }
    return ptr - buf;
}

// Десериализация запроса (аналогично для ответов)
// Здесь для краткости опускаем полную реализацию, но она генерируется аналогично.