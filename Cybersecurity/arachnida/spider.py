#!/usr/bin/env python3
import os
import sys
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# 이미지 확장자 리스트
IMG_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

def is_image_url(url):
  lower_url = url.lower()
  return any(lower_url.endswith(ext) for ext in IMG_EXTENSIONS)

def download_image(img_url, save_path):
  try:
    r = requests.get(img_url, stream=True, timeout=10)
    r.raise_for_status()
    with open(save_path, 'wb') as f:
      for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)
    print(f"[+] Downloaded: {img_url} -> {save_path}")
  except Exception as e:
    print(f"[-] Failed to download {img_url}: {e}")

def spider_crawl(url, save_dir, depth, max_depth, visited):
  # 깊이 초과 시 중단
  if depth > max_depth:
    return
  # 이미 방문한 URL이면 중단
  if url in visited:
    return
  visited.add(url)

  # 페이지 로드
  try:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
  except requests.RequestException:
    return

  soup = BeautifulSoup(r.text, 'html.parser')

  # 이미지 다운로드
  images = soup.find_all('img')
  for img in images:
    src = img.get('src')
    if src:
      img_url = urljoin(url, src)
      if is_image_url(img_url):
        filename = os.path.basename(urlparse(img_url).path)
        # 파일명이 없을 경우 스킵
        if not filename:
          continue
        # 저장 디렉토리 생성
        if not os.path.exists(save_dir):
          os.makedirs(save_dir)
        save_path = os.path.join(save_dir, filename)
        download_image(img_url, save_path)

  # 재귀 탐색 옵션이 있는 경우 하위 링크 추적
  links = soup.find_all('a')
  for link in links:
    href = link.get('href')
    if href:
      next_url = urljoin(url, href)
      spider_crawl(next_url, save_dir, depth+1, max_depth, visited)

def main():
  args = sys.argv[1:]
  if len(args) == 0:
    print("Usage: ./spider [-r -l N -p PATH] URL")
    sys.exit(1)

  # 기본값 설정
  recursive = False
  max_depth = 5
  save_dir = './data/'
  url = None

  i = 0
  while i < len(args):
    arg = args[i]
    if arg == '-r':
      recursive = True
      i += 1
    elif arg == '-l':
      i += 1
      if i >= len(args):
        print("Error: -l option requires a number")
        sys.exit(1)
      max_depth = int(args[i])
      i += 1
    elif arg == '-p':
      i += 1
      if i >= len(args):
        print("Error: -p option requires a path")
        sys.exit(1)
      save_dir = args[i]
      i += 1
    else:
      # 남는 것은 URL
      url = arg
      i += 1

  if url is None:
    print("Usage: ./spider [-r -l N -p PATH] URL")
    sys.exit(1)

  visited = set()
  if recursive:
    spider_crawl(url, save_dir, 1, max_depth, visited)
  else:
    # 재귀 옵션이 없으면 depth=1, max_depth=1로 동일
    spider_crawl(url, save_dir, 1, 1, visited)

if __name__ == '__main__':
  main()
