from src.agent import load_and_index, repl_chat


def test_index():
    db = load_and_index()

    ret = db.as_retriever(similarity_top_k=1)
    res = ret.retrieve("What is the Luxury car you have")

    for r in res:
        print(r)
        print("-" * 100)

    assert True


def test_agent():
    repl_chat()


if __name__ == "__main__":
    test_index()
    test_agent()
