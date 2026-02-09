#!/bin/bash
# 사용자 요청: DBeaver 실행 및 Oracle DB 자동 시작

# 1. Colima 상태 확인 및 시작
echo "Checking Colima Status..."
if ! colima status > /dev/null 2>&1; then
    echo "Starting Colima..."
    colima start --cpu 4 --memory 8
    if [ $? -ne 0 ]; then
        echo "Error: Failed to start Colima."
        exit 1
    fi
else
    echo "Colima is running."
fi

# 2. Oracle 컨테이너 시작
echo "Starting Oracle Container..."
CONTAINER_NAME="oracle-xe"
if ! docker start oracle-xe > /dev/null 2>&1; then
    docker start oracle
    CONTAINER_NAME="oracle"
fi
echo "Target Container: $CONTAINER_NAME"

# 3. DB 상태 확인 (Smart Check - 최대 60초)
echo "Waiting for Oracle Listener to be READY..."
MAX_RETRIES=60
COUNT=0
DB_READY=false

while [ $COUNT -lt $MAX_RETRIES ]; do
    # 컨테이너 내부에서 리스너 상태 확인
    STATUS=$(docker exec $CONTAINER_NAME lsnrctl status 2>/dev/null)
    
    # "Instance "xe", status READY" 또는 유사한 READY 상태 감지
    if echo "$STATUS" | grep -q "status READY"; then
        echo "Oracle Listener is READY!"
        DB_READY=true
        break
    fi

    echo "Waiting for DB... ($COUNT/$MAX_RETRIES)"
    sleep 1
    COUNT=$((COUNT+1))
done

if [ "$DB_READY" = true ]; then
    echo "Oracle DB Ready! (Fast Boot Completed)"
else
    echo "Warning: Oracle DB timed out or not ready."
    echo "Trying to proceed anyway..."
fi

# 4. DBeaver 종료 및 재시작 (깨끗한 연결 보장)
echo ""
echo "Restarting DBeaver..."

pkill -9 -f "DBeaver" 2>/dev/null
pkill -9 -f "dbeaver" 2>/dev/null
sleep 2

# 5. 연결 인수 구성
# 전달받은 연결 이름들로 DBeaver 실행
if [ "$#" -gt 0 ]; then
    echo "Opening connections: $@"
    # 각 연결을 순차적으로 열기
    for name in "$@"; do
        echo "  - $name"
    done
    
    # DBeaver CLI: -con "name=연결이름|connect=true"
    # 여러 연결을 열려면 각각 -con 옵션 사용
    ARGS=""
    for name in "$@"; do
        ARGS="$ARGS -con name=$name|connect=true"
    done
    
    open -a DBeaver --args $ARGS
else
    # 인수 없으면 그냥 DBeaver만 열기
    open -a DBeaver
fi

echo ""
echo "========================================"
echo "  DBeaver가 시작되었습니다."
echo "========================================"

exit 0
