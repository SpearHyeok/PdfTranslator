# PdfTranslator
pdf 번역기

현재 영어 -> 한국어만 가능함.
타 언어로 적용은 쉽지만, 할 계획은 없음

개인적인 공부를 위해 논문, 원서 번역용으로 제작한 프로그램입니다.

준비물: 결과물로 원하는 폰트.ttf 파일, DeepL 인증키, 번역을 원하는 pdf, 구글의 tesseract를 설치

pytesseract, tkinter, PIL, PyMuPDF등을 사용하고있습니다.


~~~~~사용법~~~~~
사용법

원하는 폰트를 준비하고
https://www.deepl.com/에서 api키를 발급받습니다.
폰트는 스크립트와 같은 경로에 두고
스크립트 최상단에서 폰트 경로와 api키를 적용합니다.

pdf 문서를 불러온 후
번역을 원하는 구역을 드래그로 페이지마다 설정해줘야합니다.
Submit 버튼을 누르고 기다립니다.

작업이 완료되면 드래그로 만들었던 구역에서 문자 영역을 잘 캐치했는지 확인
모든 페이지에서 오탈자를 확인합니다.
이때 오른쪽에 나타나는 텍스트 박스 영역은 박스내 문자열: (좌상단 좌표, 우하단 좌표)로 이루어져 있습니다.

오탈자나, 영역 변경이 필요하다면 오른쪽의 텍스트 박스에서 수정후 Edit 버튼을 누르면 현재 페이지에 적용됩니다.
오탈자 수정이 모든 페이지에서 끝나면 translate 버튼을 눌러 번역을 시작합니다.
완료되면 결과물이 화면에 표시됩니다.

마지막으로 오탈자를 수정합니다, 현재 폰트 크기를 직접 조절하는 기능은 지원하지않습니다.
영역 내부에서 최대로 채우는 방식으로 적용되고 있기에 좌표를 조절하는식으로 사용하면 됩니다.

수정이 완료되면 Export 버튼을 누릅니다.

결과물은 Exported_원래이름.pdf 로 저장됩니다.

~~~~~~~~~~~~~~~~~~~~~~

참고사항

처음 드래그로 사각박스를 지정할때 잘못 지정한 사각상자는 우클릭을 통해 지울 수 있습니다.

'문자열 :(a,b,c,d) 줄바꿈' 을 기준으로 상자를 인식하고있으니 수정시에 형태를 꼭지켜야합니다.
처음과 끝의 공백은 인식하지 않습니다.
아예 지우면 영역이 사라집니다.
Submit 버튼은 사각영역을 기준으로 새롭게 텍스트를 인식하는 버튼입니다.
잘못 누르면 오탈자 수정이 모두 날아가버릴 염려가 있습니다. 주의!

정상적으로 종료시에는 작업 상태를 파일이름.rectangles 로 저장하고 있습니다.
작업 현황을 저장하고 싶다면 정상적으로 종료하세요.


사용예

<img width="1673" alt="스크린샷 2024-03-29 오전 12 19 36" src="https://github.com/SpearHyeok/PdfTranslator/assets/149657377/1bdd1f90-185e-49e0-bc98-1331070f160a">
<img width="1673" alt="스크린샷 2024-03-29 오전 12 19 41" src="https://github.com/SpearHyeok/PdfTranslator/assets/149657377/71f0319e-8e00-4565-a58b-5e454db85ee7">
<img width="1673" alt="스크린샷 2024-03-29 오전 12 19 46" src="https://github.com/SpearHyeok/PdfTranslator/assets/149657377/58f1460c-bb62-4257-9e43-a66aea47dc77">
<img width="1673" alt="스크린샷 2024-03-29 오전 12 22 25" src="https://github.com/SpearHyeok/PdfTranslator/assets/149657377/7b9e609f-4e01-40fe-a41f-d3d94115d15f">

<img width="1764" alt="스크린샷 2024-03-29 오전 12 14 57" src="https://github.com/SpearHyeok/PdfTranslator/assets/149657377/2f76dc92-87f1-4929-8702-6f6b5529eea9">
<img width="1764" alt="스크린샷 2024-03-29 오전 12 14 53" src="https://github.com/SpearHyeok/PdfTranslator/assets/149657377/894403c5-e357-4493-be5e-008e594cd518">
<img width="1764" alt="스크린샷 2024-03-29 오전 12 15 18" src="https://github.com/SpearHyeok/PdfTranslator/assets/149657377/63fd5998-8340-4b23-8587-0e1da4ade584">
<img width="1764" alt="스크린샷 2024-03-29 오전 12 15 22" src="https://github.com/SpearHyeok/PdfTranslator/assets/149657377/1803c9e3-b520-4ae4-b680-788afb20906f">
<img width="1764" alt="스크린샷 2024-03-29 오전 12 16 13" src="https://github.com/SpearHyeok/PdfTranslator/assets/149657377/f566adca-3ab4-4d77-8301-1be97ad9182c">
<img width="1764" alt="스크린샷 2024-03-29 오전 12 16 53" src="https://github.com/SpearHyeok/PdfTranslator/assets/149657377/3c5ee407-6239-46e3-9546-5fb8c5f67302">
<img width="1764" alt="스크린샷 2024-03-29 오전 12 16 59" src="https://github.com/SpearHyeok/PdfTranslator/assets/149657377/3e581c7c-6fca-412f-8f07-2d4a40b5b275">




