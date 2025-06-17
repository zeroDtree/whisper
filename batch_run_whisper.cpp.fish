#!/usr/bin/env fish
set -l ARGS (getopt -o m:f:l:to:i: -l model:,file:,language:,output_txt,--output-dir:,input_dir -- $argv)

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
        case -o --output-dir
            set output_dir $argv[2]
            set argv $argv[3..-1]
        case -i --input-dir
            set input_dir $argv[2]
            set argv $argv[3..-1]
        case --
            set argv $argv[2..-1]
            break
        case '*'
            echo "Unknown option: $argv[1]"
            exit 1
    end
end


for file in (find $input_dir -type f)
    echo "Processing: $file"
    set relative_path (string replace -r '^data/' '' -- $file)
    set out_dir (dirname $output_dir/$relative_path)
    set out_file (string replace -r '\.[^\.]+$' '' -- outputs/$relative_path)

    mkdir -p $out_dir

    ./run_whisper.cpp.fish -m $model -f $file -l $language -o $out_file -t 
end