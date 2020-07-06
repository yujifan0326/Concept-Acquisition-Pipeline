while getopts "l:" arg
do
  case $arg in
  l)
    case $OPTARG in
    en)
      cmd="bert-serving-start -model_dir ../bert-model/uncased_L-12_H-768_A-12 -num_worker=1"
      echo $cmd
      ;;
    zh)
      cmd="bert-serving-start -model_dir ../bert-model/chinese_L-12_H-768_A-12 -num_worker=1"
      echo $cmd
      ;;
    *)
      echo "unknown value $OPTARG of arg t"
      ;;
    esac
    ;;
  *)
    ;;
  esac
done
$cmd
