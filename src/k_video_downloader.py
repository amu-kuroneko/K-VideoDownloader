#!/usr/bin/env python
# --- coding: utf-8 ---

from animenova.AnimeNovaRunner import AnimeNovaRunner

runners = [AnimeNovaRunner]

while True:
    try:
        input_data = input('Input URL > ').strip()
    except EOFError:
        print("\nBye.")
        break
    if input_data == 'exit':
        print('Bye.')
        break
    elif input_data != '':
        for runner in runners:
            if runner.check(input_data):
                runner(input_data).run()
                break
        else:
            print('入力されたURLはサポートしていません')

