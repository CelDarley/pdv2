FROM kivy/buildozer

WORKDIR /app
COPY . .

CMD ["buildozer", "android", "debug"] 