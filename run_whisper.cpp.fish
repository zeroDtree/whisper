#!/usr/bin/env fish
set -l ARGS (getopt -o m:f:l:to: -l model:,file:,language:,output_txt,--output-file: -- $argv)

echo $ARGS

if test $status -ne 0
    echo "Failed to parse arguments"
    exit 1
end

eval set -- argv $ARGS

echo $argv

while test (count $argv) -gt 0
    switch $argv[1]
        case -m --model
            set model $argv[2]
            set argv $argv[3..-1]
        case -f --file
            set file $argv[2]
            set argv $argv[3..-1]
        case -l --language
            set language $argv[2]
            set argv $argv[3..-1]
        case -t --output_txt
            set output_txt_flag --output-txt
            set argv $argv[2..-1]
        case -o --output-file
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

whisper-cli -m "/home/zengls/software/whisper.cpp/models/ggml-$model.bin" -f $file --language $language $output_txt_flag --output-file $output_file
