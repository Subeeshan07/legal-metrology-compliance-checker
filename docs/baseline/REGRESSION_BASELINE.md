\# Regression Test Baseline



\*\*Task:\*\* 0.4 — Regression and Smoke-Test Baseline  

\*\*Project:\*\* Legal Metrology Compliance Checker



\## 1. Purpose



This regression baseline protects the existing behaviour of the Legal

Metrology Compliance Checker before major architectural refactoring begins.



The objective is to ensure that future refactoring does not accidentally

break functionality that currently works.



---



\## 2. Test Coverage



The project currently contains two complementary test suites.



\### Original Prototype Tests



The original `test\_app.py` contains 9 tests covering:



\- Products API

\- Rules API

\- Scan API

\- Statistics API

\- Compliant declaration evaluation

\- Non-compliant declaration evaluation

\- Non-standard quantity units

\- Dataset integrity

\- Tesseract OCR execution



\### Regression Baseline Tests



`tests/test\_regression\_baseline.py` adds 10 regression/smoke tests covering:



\- Flask application construction

\- Home-page availability

\- Statistics API contract

\- Products API availability

\- Rules API contract

\- Dataset loading

\- Dataset-file availability

\- Known compliant preset scanning

\- Invalid scan request handling

\- Tesseract OCR availability



---



\## 3. Baseline Result



At the completion of Task 0.4:



\- Original tests passed: 9/9

\- Regression tests passed: 10/10

\- Total tests passed: 19/19

\- Tesseract OCR detected successfully

\- Dataset loaded successfully

\- Core application routes remained operational



Final result:



```text

Ran 19 tests

OK

