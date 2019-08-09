TAG=${1:-alpha}
echo "python send_fit_job.py --server bumps_gui --port 4567 --tag $TAG -y curv_fit.py curv_fit_1.py curv_fit_2.py curv_fit_3.py"
python send_fit_job.py --server bumps_gui --port 4567 --tag $TAG -y curv_fit.py curv_fit_1.py curv_fit_2.py curv_fit_3.py&

echo "python send_fit_job.py --server bumps_gui --port 4567 --algorithm dream --tag dream_$TAG -y curv_fit.py curv_fit_1.py curv_fit_2.py curv_fit_3.py"
python send_fit_job.py --server bumps_gui --port 4567 --algorithm dream --tag dream_$TAG -y curv_fit.py curv_fit_1.py curv_fit_2.py curv_fit_3.py&

echo "python send_fit_job.py --server bumps_gui --port 4567 --command tags -y"
python send_fit_job.py --server bumps_gui --port 4567 --command tags -y

echo "python send_fit_job.py --server bumps_gui --port 4567 --tag $TAG -y --command status"
python send_fit_job.py --server bumps_gui --port 4567 --tag dream_$TAG -y --command status

echo "python send_fit_job.py --server bumps_gui --port 4567 --tag $TAG -y --command status"
python send_fit_job.py --server bumps_gui --port 4567 --tag dream_$TAG -y --command status