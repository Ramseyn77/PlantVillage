

## Description



## Features


## Prerequisite 



## Installation

```
git clone https://github.com/szeyu/streamlit-authentication-template.git
```

```
cd PlantVillage
```

```
conda create -n <VENV> python=3.10
```

```
conda activate <VENV>
```

```
pip install -r requirements.txt
```

## Setup

1. Set the variable in `.env`
    * `sender_mail`: The email you wanna use to send to user for OTP verification
    * `sender_mail_pass`: This should be your App Password if 2FA is enabled 

2.  * To create DB:
        ```
        python -m databases.models
        ```

3. Run the code!
    ```
    streamlit run app.py
    ```