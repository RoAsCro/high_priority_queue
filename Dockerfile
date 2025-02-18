FROM python
WORKDIR /app
COPY ./teams /app
RUN pip3 install -r ./requirements.txt
CMD ["python","./teams.py"]