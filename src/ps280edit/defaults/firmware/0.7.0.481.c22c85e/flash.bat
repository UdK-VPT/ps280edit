esptool erase_flash
esptool write_flash 0x0 bootloader.bin
esptool write_flash 0x8000 partition-table.bin
esptool write_flash 0x10000 pikk-sense-esp32-main.bin
pause
