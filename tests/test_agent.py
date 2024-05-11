from src.agent import load_and_index


def test_agent():
    index = load_and_index()
    retriever = index.as_retriever(similarity_top_k=1)
    resp = retriever.retrieve("What is the horsepower of Nova Hybrid")

    for r in resp:
        print(r)

    assert True


if __name__ == "__main__":
    test_agent()
