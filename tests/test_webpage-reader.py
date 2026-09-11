from tools.webpage_reader import WebpageReader


def main():

    reader = WebpageReader()

    url = "https://arxiv.org/abs/2003.08934"

    print("正在读取网页...")
    print(url)

    content = reader.read(url)

    print("\n读取成功！")
    print("=" * 60)

    print(content[:500])


if __name__ == "__main__":
    main()