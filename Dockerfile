FROM python
WORKDIR /app
ADD ./teams/requirements.txt /app/requirements.txt
RUN pip3 install -r ./requirements.txt
COPY ./teams /app
EXPOSE 5001
CMD ["gunicorn", "--bind","0.0.0.0:5001", "teams_consumer:run()"]