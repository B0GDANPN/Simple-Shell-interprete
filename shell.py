from io import StringIO
from sys import stdin, stdout
from os.path import isdir, relpath, join, exists, abspath
from os import chdir, mkdir, listdir, getcwd
from typing import TextIO
from re import findall


def solution(script: TextIO, output: TextIO) -> None:
    def print_to_stream(func, args: list, redirection=None):
        out = args[-1]
        if output == out:
            func(*args[:-1], out)
        else:
            with open(out, 'a+', encoding="utf-8") as out_new:
                if redirection == ">":
                    out_new.flush()
                func(*args[:-1], out_new)

    def pwd(output=output):
        print(getcwd(), file=output)

    def cd(dir=None, output=output):
        dir = dir or ' '
        if not (exists(join(getcwd(), dir))):
            print(
                f"cannot change directory {dir}: directory is not exist or input is not directory", file=output)
        else:
            chdir(dir)

    def mkdirectory(dir=None, output=output):
        dir = dir or ' '
        if exists(join(getcwd(), dir)):
            print(
                f"cannot create directory {dir}: file exists", file=output)
        else:
            mkdir(dir)

    def ls(name_dir=None, output=output):
        name_dir = name_dir or getcwd()
        print(' '.join(sorted(listdir(name_dir))), file=output)

    def uni_cat(args: list, reversd=False, output=output):
        for file in args:
            with open(file, 'r', encoding="utf-8") as fil:
                for line in (reversed(fil.readlines()) if reversd else fil):
                    print(line, end='', file=output)

    def prefix(options=[], file_or_dir=None):
        file_or_dir = file_or_dir or getcwd()
        res = ''
        if len(options) and options[-1] == 'f':
            res = relpath(abspath(file_or_dir), getcwd()) + ':'
        return res

    def grep(options: list, pattern, file_or_dir=None, output=output):
        file_or_dir = file_or_dir or getcwd()
        if '-r' in options:
            if isdir(file_or_dir):
                list_files = sorted(listdir(file_or_dir))
                for elem in list_files:  # type: ignore
                    grep(options, pattern, f"{file_or_dir}/{elem}", output)
            else:
                grep([x for x in options if x != '-r'] + ['f'],
                     pattern, file_or_dir, output)
            return
        if '-c' in options:
            with open(file_or_dir, 'r', encoding="utf-8") as fil:
                count = 0
                for line in fil:
                    if findall(pattern, line):
                        count += 1
                print(prefix(options, file_or_dir) + str(count), file=output)
        else:
            with open(abspath(file_or_dir), 'r', encoding="utf-8") as fil:

                for line in fil:
                    if findall(pattern, line):
                        print(prefix(options, file_or_dir) +
                              line, end='', file=output)

    def parse_input(line: str):
        input = line.split()
        stack = []
        for el in input:
            res = [el]
            if ">>" in el:
                if el[0] == '>':
                    res = [">>", el[2:]]
                elif el[-1] == '>':
                    res = [el[:-2], ">>"]
            elif ">" in el:
                if el[0] == '>':
                    res = [">", el[1:]]
                elif el[-1] == '>':
                    res = [el[:-1], ">"]
            stack.extend(list(filter(None, res)))
        return stack
    for line in script:
        command_line = parse_input(line)
        if command_line[0] == "pwd":
            if len(command_line) > 1:  # 0pwd 1> 2dir
                print_to_stream(
                    func=pwd, args=[command_line[2]], redirection=command_line[1])
            else:
                print_to_stream(func=pwd, args=[output])
        elif command_line[0] == "cd":  # 0cd 1dir 2> 3out  ||   0cd 1dir
            if len(command_line) > 2:
                print_to_stream(
                    cd, [command_line[1], command_line[3]], redirection=command_line[2])
            else:
                print_to_stream(cd, [command_line[1], output])
        elif command_line[0] == "mkdir":  # 0cd 1dir 2> 3out  ||   0cd 1dir
            if len(command_line) > 2:
                print_to_stream(
                    mkdirectory, [command_line[1], command_line[3]], redirection=command_line[2])
            else:
                print_to_stream(mkdirectory, [command_line[1], output])
        elif command_line[0] == "ls":
            if len(command_line) == 1:  # 0ls
                print_to_stream(ls, [None, output])
            elif len(command_line) == 2:  # 0ls 1dir
                print_to_stream(ls, [command_line[1], output])
            elif len(command_line) == 4:  # 0ls 1dir 2> 3dir
                print_to_stream(
                    ls, [command_line[1], command_line[3]], redirection=command_line[2])
        elif command_line[0] == "cat" or command_line[0] == "tac":
            list_files = []
            i = 1
            flag = True
            while i < len(command_line):
                if command_line[i] != ">" and command_line[i] != ">>":
                    list_files.append(command_line[i])
                else:
                    print_to_stream(
                        uni_cat, [list_files, (True if command_line[0] == "tac" else False), command_line[i + 1]], redirection=command_line[i])
                    flag = False
                    break
                i += 1
            if flag and (i == len(command_line)):
                print_to_stream(
                    uni_cat, [list_files, (True if command_line[0] == "tac" else False), output])
        elif command_line[0] == "grep":
            options = []
            index_pattern = 0
            type_output = None
            grep_out = output
            for i in range(len(command_line)):
                if command_line[i] == ">" or command_line[i] == ">>":
                    type_output = command_line[i]
                    grep_out = command_line[i+1]
                    command_line = command_line[:-2]
                    break
            file_or_dir = getcwd()
            assert command_line[0] == 'grep'
            command_line = command_line[1:]
            was_pattern = False
            pattern = ''
            for elem in command_line:
                if elem == '-r' or elem == '-c':
                    options.append(elem)
                elif not (was_pattern):
                    pattern = elem.replace('"', '')
                    was_pattern = True
                else:
                    file_or_dir = elem
            print_to_stream(
                grep, [options, pattern, file_or_dir, grep_out], redirection=type_output)


if __name__ == '__main__':
    print("$ ", end="")
    for line in stdin:
        solution(StringIO(line), stdout)
        print("$ ", end="")
