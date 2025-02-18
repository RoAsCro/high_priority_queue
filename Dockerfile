FROM python
WORKDIR /app
COPY ./teams /app
EXPOSE 5001
RUN pip3 install -r ./requirements.txt
CMD ["gunicorn", "--bind","0.0.0.0:5001", "teams:run()"]