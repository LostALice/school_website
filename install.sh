now=$(date +"%s")

docker image build -t pms-backend:$now .

echo "\e[1;35m Build successfully \e[0m"
