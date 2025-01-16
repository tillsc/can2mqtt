#!/usr/bin/python3

from can2mqtt.app import load_config, load_dbc_db, main_program

if __name__ == '__main__':
  config = load_config()
  dbc_db = load_dbc_db(config['dbc_files'])
  main_program(config, dbc_db)
