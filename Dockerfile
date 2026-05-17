# Python පදනම් කරගත් ඉමේජ් එකක් භාවිතා කිරීම
FROM python:3.11-slim

# අවශ්‍ය කරන System Packages (FFmpeg ඇතුළුව) ඉන්ස්ටෝල් කිරීම
RUN apt-get update && apt-get install -y ffmpeg

# අපේ කෝඩ් එක දාන්න සර්වර් එකේ ෆෝල්ඩර් එකක් හැදීම
WORKDIR /app

# Requirements ෆයිල් එක කොපි කරලා Python packages ඉන්ස්ටෝල් කිරීම
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# අපේ අනිත් කෝඩ් ඔක්කොම කොපි කිරීම
COPY . .

# Bot ව Run කරන කමාන්ඩ් එක
CMD ["python", "main.py"]
