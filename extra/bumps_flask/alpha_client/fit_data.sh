TAG=${1:-foo}
#ARG2=${2:-bar}
#ARG3=${3:-1}
#ARG4=${4:-$(date)}

# echo "$TAG"
#echo "$ARG2"
#echo "$ARG3"
#echo "$ARG4"

#TAG=${1,-alpha}
#echo "$TAG"
echo "python send_fit_job.py --server bumps_gui --port 4567 --tag $TAG -y --command data"
python send_fit_job.py --server bumps_gui --port 4567 --tag $TAG -y --command data
