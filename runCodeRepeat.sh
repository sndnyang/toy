
compare() {

    length=${#flist[@]}

    echo $length

    for ((i = 0; i < $length; i++))
    do
        for (( j = i+1; j < $length; j++))
        do
            echo ${flist[i]} ${flist[j]}
        done
    done


}

function main() {

    for ((i = 1; i < 10; i++))
    do
        cd dataset/codeplagiarism/zdf;
        flist=($(ls $i* 2>/dev/null )) 
        echo ${flist[@]}
        cd -;
    done
}

main
