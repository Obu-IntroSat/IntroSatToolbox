/**
 * Автоматически сгенерированная реализация протокола.
 * Не редактируйте вручную.
 */
#include "protocol.h"
#include <string.h>

// Вспомогательные функции для упаковки/распаковки (little-endian)
static inline void pack_uint8(uint8_t val, uint8_t* buf) { *buf = val; }
static inline void pack_uint16(uint16_t val, uint8_t* buf) { memcpy(buf, &val, 2); }
static inline void pack_uint32(uint32_t val, uint8_t* buf) { memcpy(buf, &val, 4); }
static inline void pack_bool(bool val, uint8_t* buf) { *buf = val ? 1 : 0; }

static inline uint8_t unpack_uint8(const uint8_t* buf) { return *buf; }
static inline uint16_t unpack_uint16(const uint8_t* buf) { uint16_t v; memcpy(&v, buf, 2); return v; }
static inline uint32_t unpack_uint32(const uint8_t* buf) { uint32_t v; memcpy(&v, buf, 4); return v; }
static inline bool unpack_bool(const uint8_t* buf) { return *buf != 0; }

// ---------- Сериализация/десериализация запросов ----------
uint8_t serialize_RequestGetVersion(const RequestGetVersion* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    return ptr - buf;
}

void deserialize_RequestGetVersion(const uint8_t* buf, RequestGetVersion* req) {
    const uint8_t* ptr = buf;
    (void)ptr;
}
uint8_t serialize_RequestGetStatus(const RequestGetStatus* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    return ptr - buf;
}

void deserialize_RequestGetStatus(const uint8_t* buf, RequestGetStatus* req) {
    const uint8_t* ptr = buf;
    (void)ptr;
}
uint8_t serialize_RequestReset(const RequestReset* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    return ptr - buf;
}

void deserialize_RequestReset(const uint8_t* buf, RequestReset* req) {
    const uint8_t* ptr = buf;
    (void)ptr;
}
uint8_t serialize_RequestGpioInitOutput(const RequestGpioInitOutput* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->pin, ptr);
    ptr += 1;
    pack_bool(req->initial_state, ptr);
    ptr += 1;
    pack_bool(req->open_drain, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_RequestGpioInitOutput(const uint8_t* buf, RequestGpioInitOutput* req) {
    const uint8_t* ptr = buf;
    req->pin = unpack_uint8(ptr);
    ptr += 1;
    req->initial_state = unpack_bool(ptr);
    ptr += 1;
    req->open_drain = unpack_bool(ptr);
    ptr += 1;
    (void)ptr;
}
uint8_t serialize_RequestGpioInitInput(const RequestGpioInitInput* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->pin, ptr);
    ptr += 1;
    pack_uint8(req->pull, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_RequestGpioInitInput(const uint8_t* buf, RequestGpioInitInput* req) {
    const uint8_t* ptr = buf;
    req->pin = unpack_uint8(ptr);
    ptr += 1;
    req->pull = unpack_uint8(ptr);
    ptr += 1;
    (void)ptr;
}
uint8_t serialize_RequestGpioSet(const RequestGpioSet* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->pin, ptr);
    ptr += 1;
    pack_bool(req->value, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_RequestGpioSet(const uint8_t* buf, RequestGpioSet* req) {
    const uint8_t* ptr = buf;
    req->pin = unpack_uint8(ptr);
    ptr += 1;
    req->value = unpack_bool(ptr);
    ptr += 1;
    (void)ptr;
}
uint8_t serialize_RequestGpioRead(const RequestGpioRead* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->pin, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_RequestGpioRead(const uint8_t* buf, RequestGpioRead* req) {
    const uint8_t* ptr = buf;
    req->pin = unpack_uint8(ptr);
    ptr += 1;
    (void)ptr;
}
uint8_t serialize_RequestGpioDeinit(const RequestGpioDeinit* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->pin, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_RequestGpioDeinit(const uint8_t* buf, RequestGpioDeinit* req) {
    const uint8_t* ptr = buf;
    req->pin = unpack_uint8(ptr);
    ptr += 1;
    (void)ptr;
}
uint8_t serialize_RequestAdcRead(const RequestAdcRead* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->channel, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_RequestAdcRead(const uint8_t* buf, RequestAdcRead* req) {
    const uint8_t* ptr = buf;
    req->channel = unpack_uint8(ptr);
    ptr += 1;
    (void)ptr;
}
uint8_t serialize_RequestEepromRead(const RequestEepromRead* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint16(req->address, ptr);
    ptr += 2;
    pack_uint8(req->len, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_RequestEepromRead(const uint8_t* buf, RequestEepromRead* req) {
    const uint8_t* ptr = buf;
    req->address = unpack_uint16(ptr);
    ptr += 2;
    req->len = unpack_uint8(ptr);
    ptr += 1;
    (void)ptr;
}
uint8_t serialize_RequestI2cProbe(const RequestI2cProbe* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->address, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_RequestI2cProbe(const uint8_t* buf, RequestI2cProbe* req) {
    const uint8_t* ptr = buf;
    req->address = unpack_uint8(ptr);
    ptr += 1;
    (void)ptr;
}
uint8_t serialize_RequestI2cReadRegister(const RequestI2cReadRegister* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->address, ptr);
    ptr += 1;
    pack_uint8(req->reg, ptr);
    ptr += 1;
    pack_uint8(req->len, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_RequestI2cReadRegister(const uint8_t* buf, RequestI2cReadRegister* req) {
    const uint8_t* ptr = buf;
    req->address = unpack_uint8(ptr);
    ptr += 1;
    req->reg = unpack_uint8(ptr);
    ptr += 1;
    req->len = unpack_uint8(ptr);
    ptr += 1;
    (void)ptr;
}
uint8_t serialize_RequestI2cWriteRegister(const RequestI2cWriteRegister* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->address, ptr);
    ptr += 1;
    pack_uint8(req->reg, ptr);
    ptr += 1;
    pack_uint8(req->data_len, ptr);
    ptr += 1;
    memcpy(ptr, req->data, sizeof(req->data));
    ptr += sizeof(req->data);
    return ptr - buf;
}

void deserialize_RequestI2cWriteRegister(const uint8_t* buf, RequestI2cWriteRegister* req) {
    const uint8_t* ptr = buf;
    req->address = unpack_uint8(ptr);
    ptr += 1;
    req->reg = unpack_uint8(ptr);
    ptr += 1;
    req->data_len = unpack_uint8(ptr);
    ptr += 1;
    memcpy(req->data, ptr, sizeof(req->data));
    ptr += sizeof(req->data);
    (void)ptr;
}
uint8_t serialize_RequestI2cWrite(const RequestI2cWrite* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->address, ptr);
    ptr += 1;
    pack_uint8(req->data_len, ptr);
    ptr += 1;
    memcpy(ptr, req->data, sizeof(req->data));
    ptr += sizeof(req->data);
    return ptr - buf;
}

void deserialize_RequestI2cWrite(const uint8_t* buf, RequestI2cWrite* req) {
    const uint8_t* ptr = buf;
    req->address = unpack_uint8(ptr);
    ptr += 1;
    req->data_len = unpack_uint8(ptr);
    ptr += 1;
    memcpy(req->data, ptr, sizeof(req->data));
    ptr += sizeof(req->data);
    (void)ptr;
}
uint8_t serialize_RequestI2cRead(const RequestI2cRead* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->address, ptr);
    ptr += 1;
    pack_uint8(req->len, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_RequestI2cRead(const uint8_t* buf, RequestI2cRead* req) {
    const uint8_t* ptr = buf;
    req->address = unpack_uint8(ptr);
    ptr += 1;
    req->len = unpack_uint8(ptr);
    ptr += 1;
    (void)ptr;
}
uint8_t serialize_RequestSpiSend(const RequestSpiSend* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->spi_num, ptr);
    ptr += 1;
    pack_uint8(req->data_len, ptr);
    ptr += 1;
    memcpy(ptr, req->data, sizeof(req->data));
    ptr += sizeof(req->data);
    return ptr - buf;
}

void deserialize_RequestSpiSend(const uint8_t* buf, RequestSpiSend* req) {
    const uint8_t* ptr = buf;
    req->spi_num = unpack_uint8(ptr);
    ptr += 1;
    req->data_len = unpack_uint8(ptr);
    ptr += 1;
    memcpy(req->data, ptr, sizeof(req->data));
    ptr += sizeof(req->data);
    (void)ptr;
}
uint8_t serialize_RequestSpiReceive(const RequestSpiReceive* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->spi_num, ptr);
    ptr += 1;
    pack_uint8(req->len, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_RequestSpiReceive(const uint8_t* buf, RequestSpiReceive* req) {
    const uint8_t* ptr = buf;
    req->spi_num = unpack_uint8(ptr);
    ptr += 1;
    req->len = unpack_uint8(ptr);
    ptr += 1;
    (void)ptr;
}
uint8_t serialize_RequestSpiExchange(const RequestSpiExchange* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->spi_num, ptr);
    ptr += 1;
    pack_uint8(req->tx_len, ptr);
    ptr += 1;
    memcpy(ptr, req->tx_data, sizeof(req->tx_data));
    ptr += sizeof(req->tx_data);
    return ptr - buf;
}

void deserialize_RequestSpiExchange(const uint8_t* buf, RequestSpiExchange* req) {
    const uint8_t* ptr = buf;
    req->spi_num = unpack_uint8(ptr);
    ptr += 1;
    req->tx_len = unpack_uint8(ptr);
    ptr += 1;
    memcpy(req->tx_data, ptr, sizeof(req->tx_data));
    ptr += sizeof(req->tx_data);
    (void)ptr;
}
uint8_t serialize_RequestUartSend(const RequestUartSend* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->uart_num, ptr);
    ptr += 1;
    pack_uint8(req->data_len, ptr);
    ptr += 1;
    memcpy(ptr, req->data, sizeof(req->data));
    ptr += sizeof(req->data);
    return ptr - buf;
}

void deserialize_RequestUartSend(const uint8_t* buf, RequestUartSend* req) {
    const uint8_t* ptr = buf;
    req->uart_num = unpack_uint8(ptr);
    ptr += 1;
    req->data_len = unpack_uint8(ptr);
    ptr += 1;
    memcpy(req->data, ptr, sizeof(req->data));
    ptr += sizeof(req->data);
    (void)ptr;
}
uint8_t serialize_RequestUartReceive(const RequestUartReceive* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->uart_num, ptr);
    ptr += 1;
    pack_uint16(req->timeout_ms, ptr);
    ptr += 2;
    pack_uint8(req->max_len, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_RequestUartReceive(const uint8_t* buf, RequestUartReceive* req) {
    const uint8_t* ptr = buf;
    req->uart_num = unpack_uint8(ptr);
    ptr += 1;
    req->timeout_ms = unpack_uint16(ptr);
    ptr += 2;
    req->max_len = unpack_uint8(ptr);
    ptr += 1;
    (void)ptr;
}
uint8_t serialize_RequestInitI2c(const RequestInitI2c* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->i2c_num, ptr);
    ptr += 1;
    pack_uint8(req->scl_pin, ptr);
    ptr += 1;
    pack_uint8(req->sda_pin, ptr);
    ptr += 1;
    pack_uint32(req->speed, ptr);
    ptr += 4;
    return ptr - buf;
}

void deserialize_RequestInitI2c(const uint8_t* buf, RequestInitI2c* req) {
    const uint8_t* ptr = buf;
    req->i2c_num = unpack_uint8(ptr);
    ptr += 1;
    req->scl_pin = unpack_uint8(ptr);
    ptr += 1;
    req->sda_pin = unpack_uint8(ptr);
    ptr += 1;
    req->speed = unpack_uint32(ptr);
    ptr += 4;
    (void)ptr;
}
uint8_t serialize_RequestDeinitI2c(const RequestDeinitI2c* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->i2c_num, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_RequestDeinitI2c(const uint8_t* buf, RequestDeinitI2c* req) {
    const uint8_t* ptr = buf;
    req->i2c_num = unpack_uint8(ptr);
    ptr += 1;
    (void)ptr;
}
uint8_t serialize_RequestInitSpi(const RequestInitSpi* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->spi_num, ptr);
    ptr += 1;
    pack_uint32(req->speed, ptr);
    ptr += 4;
    pack_uint8(req->mode, ptr);
    ptr += 1;
    pack_uint8(req->bit_order, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_RequestInitSpi(const uint8_t* buf, RequestInitSpi* req) {
    const uint8_t* ptr = buf;
    req->spi_num = unpack_uint8(ptr);
    ptr += 1;
    req->speed = unpack_uint32(ptr);
    ptr += 4;
    req->mode = unpack_uint8(ptr);
    ptr += 1;
    req->bit_order = unpack_uint8(ptr);
    ptr += 1;
    (void)ptr;
}
uint8_t serialize_RequestDeinitSpi(const RequestDeinitSpi* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->spi_num, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_RequestDeinitSpi(const uint8_t* buf, RequestDeinitSpi* req) {
    const uint8_t* ptr = buf;
    req->spi_num = unpack_uint8(ptr);
    ptr += 1;
    (void)ptr;
}
uint8_t serialize_RequestInitUart(const RequestInitUart* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->uart_num, ptr);
    ptr += 1;
    pack_uint32(req->baudrate, ptr);
    ptr += 4;
    pack_uint8(req->parity, ptr);
    ptr += 1;
    pack_uint8(req->stop_bits, ptr);
    ptr += 1;
    pack_uint8(req->data_bits, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_RequestInitUart(const uint8_t* buf, RequestInitUart* req) {
    const uint8_t* ptr = buf;
    req->uart_num = unpack_uint8(ptr);
    ptr += 1;
    req->baudrate = unpack_uint32(ptr);
    ptr += 4;
    req->parity = unpack_uint8(ptr);
    ptr += 1;
    req->stop_bits = unpack_uint8(ptr);
    ptr += 1;
    req->data_bits = unpack_uint8(ptr);
    ptr += 1;
    (void)ptr;
}
uint8_t serialize_RequestDeinitUart(const RequestDeinitUart* req, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(req->uart_num, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_RequestDeinitUart(const uint8_t* buf, RequestDeinitUart* req) {
    const uint8_t* ptr = buf;
    req->uart_num = unpack_uint8(ptr);
    ptr += 1;
    (void)ptr;
}

// ---------- Сериализация/десериализация ответов ----------
uint8_t serialize_ResponseVersionInfoResp(const ResponseVersionInfoResp* resp, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(resp->major, ptr);
    ptr += 1;
    pack_uint8(resp->minor, ptr);
    ptr += 1;
    pack_uint8(resp->patch, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_ResponseVersionInfoResp(const uint8_t* buf, ResponseVersionInfoResp* resp) {
    const uint8_t* ptr = buf;
    resp->major = unpack_uint8(ptr);
    ptr += 1;
    resp->minor = unpack_uint8(ptr);
    ptr += 1;
    resp->patch = unpack_uint8(ptr);
    ptr += 1;
    (void)ptr;
}
uint8_t serialize_ResponseStatusResp(const ResponseStatusResp* resp, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_bool(resp->powered, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_ResponseStatusResp(const uint8_t* buf, ResponseStatusResp* resp) {
    const uint8_t* ptr = buf;
    resp->powered = unpack_bool(ptr);
    ptr += 1;
    (void)ptr;
}
uint8_t serialize_ResponseGpioReadResp(const ResponseGpioReadResp* resp, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(resp->status, ptr);
    ptr += 1;
    pack_uint8(resp->error_code, ptr);
    ptr += 1;
    pack_bool(resp->value, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_ResponseGpioReadResp(const uint8_t* buf, ResponseGpioReadResp* resp) {
    const uint8_t* ptr = buf;
    resp->status = unpack_uint8(ptr);
    ptr += 1;
    resp->error_code = unpack_uint8(ptr);
    ptr += 1;
    resp->value = unpack_bool(ptr);
    ptr += 1;
    (void)ptr;
}
uint8_t serialize_ResponseAdcReadResp(const ResponseAdcReadResp* resp, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(resp->status, ptr);
    ptr += 1;
    pack_uint8(resp->error_code, ptr);
    ptr += 1;
    pack_uint16(resp->voltage_mv, ptr);
    ptr += 2;
    return ptr - buf;
}

void deserialize_ResponseAdcReadResp(const uint8_t* buf, ResponseAdcReadResp* resp) {
    const uint8_t* ptr = buf;
    resp->status = unpack_uint8(ptr);
    ptr += 1;
    resp->error_code = unpack_uint8(ptr);
    ptr += 1;
    resp->voltage_mv = unpack_uint16(ptr);
    ptr += 2;
    (void)ptr;
}
uint8_t serialize_ResponseEepromReadResp(const ResponseEepromReadResp* resp, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(resp->status, ptr);
    ptr += 1;
    pack_uint8(resp->error_code, ptr);
    ptr += 1;
    pack_uint8(resp->data_len, ptr);
    ptr += 1;
    memcpy(ptr, resp->data, sizeof(resp->data));
    ptr += sizeof(resp->data);
    return ptr - buf;
}

void deserialize_ResponseEepromReadResp(const uint8_t* buf, ResponseEepromReadResp* resp) {
    const uint8_t* ptr = buf;
    resp->status = unpack_uint8(ptr);
    ptr += 1;
    resp->error_code = unpack_uint8(ptr);
    ptr += 1;
    resp->data_len = unpack_uint8(ptr);
    ptr += 1;
    memcpy(resp->data, ptr, sizeof(resp->data));
    ptr += sizeof(resp->data);
    (void)ptr;
}
uint8_t serialize_ResponseI2cProbeResp(const ResponseI2cProbeResp* resp, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(resp->status, ptr);
    ptr += 1;
    pack_uint8(resp->error_code, ptr);
    ptr += 1;
    pack_bool(resp->present, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_ResponseI2cProbeResp(const uint8_t* buf, ResponseI2cProbeResp* resp) {
    const uint8_t* ptr = buf;
    resp->status = unpack_uint8(ptr);
    ptr += 1;
    resp->error_code = unpack_uint8(ptr);
    ptr += 1;
    resp->present = unpack_bool(ptr);
    ptr += 1;
    (void)ptr;
}
uint8_t serialize_ResponseI2cReadRegisterResp(const ResponseI2cReadRegisterResp* resp, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(resp->status, ptr);
    ptr += 1;
    pack_uint8(resp->error_code, ptr);
    ptr += 1;
    pack_uint8(resp->data_len, ptr);
    ptr += 1;
    memcpy(ptr, resp->data, sizeof(resp->data));
    ptr += sizeof(resp->data);
    return ptr - buf;
}

void deserialize_ResponseI2cReadRegisterResp(const uint8_t* buf, ResponseI2cReadRegisterResp* resp) {
    const uint8_t* ptr = buf;
    resp->status = unpack_uint8(ptr);
    ptr += 1;
    resp->error_code = unpack_uint8(ptr);
    ptr += 1;
    resp->data_len = unpack_uint8(ptr);
    ptr += 1;
    memcpy(resp->data, ptr, sizeof(resp->data));
    ptr += sizeof(resp->data);
    (void)ptr;
}
uint8_t serialize_ResponseI2cReadResp(const ResponseI2cReadResp* resp, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(resp->status, ptr);
    ptr += 1;
    pack_uint8(resp->error_code, ptr);
    ptr += 1;
    pack_uint8(resp->data_len, ptr);
    ptr += 1;
    memcpy(ptr, resp->data, sizeof(resp->data));
    ptr += sizeof(resp->data);
    return ptr - buf;
}

void deserialize_ResponseI2cReadResp(const uint8_t* buf, ResponseI2cReadResp* resp) {
    const uint8_t* ptr = buf;
    resp->status = unpack_uint8(ptr);
    ptr += 1;
    resp->error_code = unpack_uint8(ptr);
    ptr += 1;
    resp->data_len = unpack_uint8(ptr);
    ptr += 1;
    memcpy(resp->data, ptr, sizeof(resp->data));
    ptr += sizeof(resp->data);
    (void)ptr;
}
uint8_t serialize_ResponseSpiReceiveResp(const ResponseSpiReceiveResp* resp, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(resp->status, ptr);
    ptr += 1;
    pack_uint8(resp->error_code, ptr);
    ptr += 1;
    pack_uint8(resp->data_len, ptr);
    ptr += 1;
    memcpy(ptr, resp->data, sizeof(resp->data));
    ptr += sizeof(resp->data);
    return ptr - buf;
}

void deserialize_ResponseSpiReceiveResp(const uint8_t* buf, ResponseSpiReceiveResp* resp) {
    const uint8_t* ptr = buf;
    resp->status = unpack_uint8(ptr);
    ptr += 1;
    resp->error_code = unpack_uint8(ptr);
    ptr += 1;
    resp->data_len = unpack_uint8(ptr);
    ptr += 1;
    memcpy(resp->data, ptr, sizeof(resp->data));
    ptr += sizeof(resp->data);
    (void)ptr;
}
uint8_t serialize_ResponseSpiExchangeResp(const ResponseSpiExchangeResp* resp, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(resp->status, ptr);
    ptr += 1;
    pack_uint8(resp->error_code, ptr);
    ptr += 1;
    pack_uint8(resp->rx_len, ptr);
    ptr += 1;
    memcpy(ptr, resp->rx_data, sizeof(resp->rx_data));
    ptr += sizeof(resp->rx_data);
    return ptr - buf;
}

void deserialize_ResponseSpiExchangeResp(const uint8_t* buf, ResponseSpiExchangeResp* resp) {
    const uint8_t* ptr = buf;
    resp->status = unpack_uint8(ptr);
    ptr += 1;
    resp->error_code = unpack_uint8(ptr);
    ptr += 1;
    resp->rx_len = unpack_uint8(ptr);
    ptr += 1;
    memcpy(resp->rx_data, ptr, sizeof(resp->rx_data));
    ptr += sizeof(resp->rx_data);
    (void)ptr;
}
uint8_t serialize_ResponseUartReceiveResp(const ResponseUartReceiveResp* resp, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(resp->status, ptr);
    ptr += 1;
    pack_uint8(resp->error_code, ptr);
    ptr += 1;
    pack_uint8(resp->data_len, ptr);
    ptr += 1;
    memcpy(ptr, resp->data, sizeof(resp->data));
    ptr += sizeof(resp->data);
    return ptr - buf;
}

void deserialize_ResponseUartReceiveResp(const uint8_t* buf, ResponseUartReceiveResp* resp) {
    const uint8_t* ptr = buf;
    resp->status = unpack_uint8(ptr);
    ptr += 1;
    resp->error_code = unpack_uint8(ptr);
    ptr += 1;
    resp->data_len = unpack_uint8(ptr);
    ptr += 1;
    memcpy(resp->data, ptr, sizeof(resp->data));
    ptr += sizeof(resp->data);
    (void)ptr;
}
uint8_t serialize_ResponseGenericResp(const ResponseGenericResp* resp, uint8_t* buf) {
    uint8_t* ptr = buf;
    pack_uint8(resp->status, ptr);
    ptr += 1;
    pack_uint8(resp->error_code, ptr);
    ptr += 1;
    return ptr - buf;
}

void deserialize_ResponseGenericResp(const uint8_t* buf, ResponseGenericResp* resp) {
    const uint8_t* ptr = buf;
    resp->status = unpack_uint8(ptr);
    ptr += 1;
    resp->error_code = unpack_uint8(ptr);
    ptr += 1;
    (void)ptr;
}

// ---------- Общие функции по коду команды ----------
uint8_t serialize_request(uint8_t cmd_code, const void* req, uint8_t* buf) {
    switch (cmd_code) {
    case 0:
        return serialize_RequestGetVersion((const RequestGetVersion*)req, buf);
    case 1:
        return serialize_RequestGetStatus((const RequestGetStatus*)req, buf);
    case 2:
        return serialize_RequestReset((const RequestReset*)req, buf);
    case 100:
        return serialize_RequestGpioInitOutput((const RequestGpioInitOutput*)req, buf);
    case 101:
        return serialize_RequestGpioInitInput((const RequestGpioInitInput*)req, buf);
    case 102:
        return serialize_RequestGpioSet((const RequestGpioSet*)req, buf);
    case 103:
        return serialize_RequestGpioRead((const RequestGpioRead*)req, buf);
    case 104:
        return serialize_RequestGpioDeinit((const RequestGpioDeinit*)req, buf);
    case 105:
        return serialize_RequestAdcRead((const RequestAdcRead*)req, buf);
    case 106:
        return serialize_RequestEepromRead((const RequestEepromRead*)req, buf);
    case 107:
        return serialize_RequestI2cProbe((const RequestI2cProbe*)req, buf);
    case 108:
        return serialize_RequestI2cReadRegister((const RequestI2cReadRegister*)req, buf);
    case 109:
        return serialize_RequestI2cWriteRegister((const RequestI2cWriteRegister*)req, buf);
    case 110:
        return serialize_RequestI2cWrite((const RequestI2cWrite*)req, buf);
    case 111:
        return serialize_RequestI2cRead((const RequestI2cRead*)req, buf);
    case 112:
        return serialize_RequestSpiSend((const RequestSpiSend*)req, buf);
    case 113:
        return serialize_RequestSpiReceive((const RequestSpiReceive*)req, buf);
    case 114:
        return serialize_RequestSpiExchange((const RequestSpiExchange*)req, buf);
    case 115:
        return serialize_RequestUartSend((const RequestUartSend*)req, buf);
    case 116:
        return serialize_RequestUartReceive((const RequestUartReceive*)req, buf);
    case 120:
        return serialize_RequestInitI2c((const RequestInitI2c*)req, buf);
    case 121:
        return serialize_RequestDeinitI2c((const RequestDeinitI2c*)req, buf);
    case 122:
        return serialize_RequestInitSpi((const RequestInitSpi*)req, buf);
    case 123:
        return serialize_RequestDeinitSpi((const RequestDeinitSpi*)req, buf);
    case 124:
        return serialize_RequestInitUart((const RequestInitUart*)req, buf);
    case 125:
        return serialize_RequestDeinitUart((const RequestDeinitUart*)req, buf);
    default:
        return 0;
    }
}

void deserialize_request(uint8_t cmd_code, const uint8_t* buf, void* req) {
    switch (cmd_code) {
    case 0:
        deserialize_RequestGetVersion(buf, (RequestGetVersion*)req);
        break;
    case 1:
        deserialize_RequestGetStatus(buf, (RequestGetStatus*)req);
        break;
    case 2:
        deserialize_RequestReset(buf, (RequestReset*)req);
        break;
    case 100:
        deserialize_RequestGpioInitOutput(buf, (RequestGpioInitOutput*)req);
        break;
    case 101:
        deserialize_RequestGpioInitInput(buf, (RequestGpioInitInput*)req);
        break;
    case 102:
        deserialize_RequestGpioSet(buf, (RequestGpioSet*)req);
        break;
    case 103:
        deserialize_RequestGpioRead(buf, (RequestGpioRead*)req);
        break;
    case 104:
        deserialize_RequestGpioDeinit(buf, (RequestGpioDeinit*)req);
        break;
    case 105:
        deserialize_RequestAdcRead(buf, (RequestAdcRead*)req);
        break;
    case 106:
        deserialize_RequestEepromRead(buf, (RequestEepromRead*)req);
        break;
    case 107:
        deserialize_RequestI2cProbe(buf, (RequestI2cProbe*)req);
        break;
    case 108:
        deserialize_RequestI2cReadRegister(buf, (RequestI2cReadRegister*)req);
        break;
    case 109:
        deserialize_RequestI2cWriteRegister(buf, (RequestI2cWriteRegister*)req);
        break;
    case 110:
        deserialize_RequestI2cWrite(buf, (RequestI2cWrite*)req);
        break;
    case 111:
        deserialize_RequestI2cRead(buf, (RequestI2cRead*)req);
        break;
    case 112:
        deserialize_RequestSpiSend(buf, (RequestSpiSend*)req);
        break;
    case 113:
        deserialize_RequestSpiReceive(buf, (RequestSpiReceive*)req);
        break;
    case 114:
        deserialize_RequestSpiExchange(buf, (RequestSpiExchange*)req);
        break;
    case 115:
        deserialize_RequestUartSend(buf, (RequestUartSend*)req);
        break;
    case 116:
        deserialize_RequestUartReceive(buf, (RequestUartReceive*)req);
        break;
    case 120:
        deserialize_RequestInitI2c(buf, (RequestInitI2c*)req);
        break;
    case 121:
        deserialize_RequestDeinitI2c(buf, (RequestDeinitI2c*)req);
        break;
    case 122:
        deserialize_RequestInitSpi(buf, (RequestInitSpi*)req);
        break;
    case 123:
        deserialize_RequestDeinitSpi(buf, (RequestDeinitSpi*)req);
        break;
    case 124:
        deserialize_RequestInitUart(buf, (RequestInitUart*)req);
        break;
    case 125:
        deserialize_RequestDeinitUart(buf, (RequestDeinitUart*)req);
        break;
    default:
        break;
    }
}

uint8_t serialize_response(uint8_t cmd_code, const void* resp, uint8_t* buf) {
    switch (cmd_code) {
    case 200:
        return serialize_ResponseVersionInfoResp((const ResponseVersionInfoResp*)resp, buf);
    case 201:
        return serialize_ResponseStatusResp((const ResponseStatusResp*)resp, buf);
    case 204:
        return serialize_ResponseGpioReadResp((const ResponseGpioReadResp*)resp, buf);
    case 205:
        return serialize_ResponseAdcReadResp((const ResponseAdcReadResp*)resp, buf);
    case 206:
        return serialize_ResponseEepromReadResp((const ResponseEepromReadResp*)resp, buf);
    case 207:
        return serialize_ResponseI2cProbeResp((const ResponseI2cProbeResp*)resp, buf);
    case 208:
        return serialize_ResponseI2cReadRegisterResp((const ResponseI2cReadRegisterResp*)resp, buf);
    case 209:
        return serialize_ResponseI2cReadResp((const ResponseI2cReadResp*)resp, buf);
    case 210:
        return serialize_ResponseSpiReceiveResp((const ResponseSpiReceiveResp*)resp, buf);
    case 211:
        return serialize_ResponseSpiExchangeResp((const ResponseSpiExchangeResp*)resp, buf);
    case 212:
        return serialize_ResponseUartReceiveResp((const ResponseUartReceiveResp*)resp, buf);
    case 250:
        return serialize_ResponseGenericResp((const ResponseGenericResp*)resp, buf);
    default:
        return 0;
    }
}

void deserialize_response(uint8_t cmd_code, const uint8_t* buf, void* resp) {
    switch (cmd_code) {
    case 200:
        deserialize_ResponseVersionInfoResp(buf, (ResponseVersionInfoResp*)resp);
        break;
    case 201:
        deserialize_ResponseStatusResp(buf, (ResponseStatusResp*)resp);
        break;
    case 204:
        deserialize_ResponseGpioReadResp(buf, (ResponseGpioReadResp*)resp);
        break;
    case 205:
        deserialize_ResponseAdcReadResp(buf, (ResponseAdcReadResp*)resp);
        break;
    case 206:
        deserialize_ResponseEepromReadResp(buf, (ResponseEepromReadResp*)resp);
        break;
    case 207:
        deserialize_ResponseI2cProbeResp(buf, (ResponseI2cProbeResp*)resp);
        break;
    case 208:
        deserialize_ResponseI2cReadRegisterResp(buf, (ResponseI2cReadRegisterResp*)resp);
        break;
    case 209:
        deserialize_ResponseI2cReadResp(buf, (ResponseI2cReadResp*)resp);
        break;
    case 210:
        deserialize_ResponseSpiReceiveResp(buf, (ResponseSpiReceiveResp*)resp);
        break;
    case 211:
        deserialize_ResponseSpiExchangeResp(buf, (ResponseSpiExchangeResp*)resp);
        break;
    case 212:
        deserialize_ResponseUartReceiveResp(buf, (ResponseUartReceiveResp*)resp);
        break;
    case 250:
        deserialize_ResponseGenericResp(buf, (ResponseGenericResp*)resp);
        break;
    default:
        break;
    }
}