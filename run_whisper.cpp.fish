#!/usr/bin/env fish
set -l ARGS (getopt -o m:l:ti:o: -l model:language:output_txt,input_file:output_file: -- $argv)

if test $status -ne 0
    echo "Failed to parse arguments"
    exit 1
end

eval set -- argv $ARGS

set output_txt_flag ""

while test (count $argv) -gt 0
    switch $argv[1]
        case -m --model
            set model $argv[2]
            set argv $argv[3..-1]
        case -i --input_file
            set input_file $argv[2]
            set argv $argv[3..-1]
        case -l --language
            set language $argv[2]
            set argv $argv[3..-1]
        case -t --output_txt
            set output_txt_flag --output-txt
            set argv $argv[2..-1]
        case -o --output_file
            set output_file $argv[2]
            set argv $argv[3..-1]
        case --
            set argv $argv[2..-1]
            break
        case '*'
            echo "Unknown option: $argv[1]"
            exit 1
    end
end

whisper-cli -m "/home/zengls/software/whisper.cpp/models/ggml-$model.bin" --language $language $output_txt_flag -f $input_file --output-file $output_file
