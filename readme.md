# 얼굴 인식 시스템

이 프로젝트는 Python, OpenCV, 그리고 PyQt5를 사용하여 구축된 실시간 얼굴 인식 시스템입니다. 웹캠을 사용하여 얼굴을 감지하고 인식하며, 인식된 개인을 로깅하고 새로운 얼굴을 시스템에 추가할 수 있습니다.

## 주요 기능

- 실시간 얼굴 감지 및 인식
- 30 FPS 성능 최적화
- 인식 데이터베이스에 새로운 얼굴 추가
- 인식된 개인 로깅
- 인식 로그 조회
- 사용자 친화적인 PyQt5 GUI

## 요구 사항

- Python 3.7+
- OpenCV
- face_recognition
- PyQt5
- NumPy

전체 의존성 목록은 `requirements.txt`를 참조하세요.

## 설치 방법

1. 이 저장소를 클론합니다:
   ```
   git clone https://github.com/your-username/face-recognition-system.git
   cd face-recognition-system
   ```

2. Conda 환경을 생성하고 활성화합니다:
   ```
   conda create --name face_recognition_env python=3.8
   conda activate face_recognition_env
   ```

3. 필요한 패키지를 설치합니다:
   ```
   pip install -r requirements.txt
   ```

## 사용 방법

1. Conda 환경을 활성화합니다:
   ```
   conda activate face_recognition_env
   ```

2. 메인 스크립트를 실행합니다:
   ```
   python face_recognition_app.py
   ```

3. GUI를 사용하여 인식 시작/중지, 새로운 얼굴 추가, 로그 조회 등을 수행합니다.

## 기여하기

기여는 언제나 환영합니다! Pull Request를 자유롭게 제출해 주세요.

## 라이선스

이 프로젝트는 오픈 소스이며 [MIT 라이선스](LICENSE)에 따라 사용 가능합니다.
