\# Target Application Architecture



\*\*Project:\*\* Legal Metrology Compliance Checker  

\*\*Phase:\*\* 1 — Architecture Refactor  

\*\*Task:\*\* 1.1 — Target Modular Architecture



---



\## 1. Purpose



The existing Legal Metrology Compliance Checker began as a functional

hackathon prototype.



The prototype successfully demonstrates:



\- label scanning;

\- OCR;

\- declaration extraction;

\- compliance checking;

\- product history;

\- statistics;

\- reporting.



However, much of the application logic currently exists inside `app.py`.



As the project expands to support improved OCR, structured extraction,

versioned compliance rules, human review, authentication, APIs and persistent

storage, the monolithic structure would become increasingly difficult to

maintain and test.



The target architecture therefore separates responsibilities into clearly

defined layers.



---



\## 2. Architectural Goals



The architecture should provide:



1\. separation of concerns;

2\. testable business logic;

3\. replaceable OCR implementations;

4\. independent compliance rules;

5\. structured data models;

6\. replaceable persistence mechanisms;

7\. reusable services;

8\. maintainable API routes;

9\. configuration management;

10\. support for future mobile/API clients.



---



\## 3. Target Directory Structure



```text

legal-metrology-compliance-checker/

│

├── app.py

├── requirements.txt

├── .env.example

├── .python-version

│

├── config/

│   ├── \_\_init\_\_.py

│   └── settings.py

│

├── routes/

│   ├── \_\_init\_\_.py

│   ├── web\_routes.py

│   ├── scan\_routes.py

│   ├── product\_routes.py

│   ├── stats\_routes.py

│   └── rule\_routes.py

│

├── services/

│   ├── \_\_init\_\_.py

│   ├── ocr\_service.py

│   ├── extraction\_service.py

│   ├── compliance\_service.py

│   ├── product\_service.py

│   └── report\_service.py

│

├── repositories/

│   ├── \_\_init\_\_.py

│   └── product\_repository.py

│

├── models/

│   ├── \_\_init\_\_.py

│   ├── product.py

│   ├── compliance.py

│   └── scan\_result.py

│

├── rules/

│   ├── \_\_init\_\_.py

│   ├── declarations.py

│   └── rule\_registry.py

│

├── utils/

│   ├── \_\_init\_\_.py

│   ├── image\_utils.py

│   ├── validators.py

│   └── file\_utils.py

│

├── data/

│   └── legal\_metrology\_dataset.csv

│

├── tests/

│   ├── unit/

│   ├── integration/

│   └── regression/

│

├── templates/

├── static/

└── docs/

