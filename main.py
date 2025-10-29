import argparse
from parser import parse, parse_user_input
from resolver import resolve
import sys
import os

def print_trees(trees, visual: bool) -> None:
    if visual:
        for tree in trees:
            print(tree.pretty())
    else:
        for tree in trees:
            print(f"{tree.name}: {'True' if tree.value else 'False' if tree.value is False else 'Undetermined'}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str, help='Path to the input file')
    parser.add_argument('-v', '--visual', help='Enable visual output', action='store_true')
    parser.add_argument('-i', '--interactive', help='Enable interactive mode', action='store_true')
    args = parser.parse_args()

    if not os.path.isfile(args.path):
        print(f"File {args.path} does not exist.")
        sys.exit(1)
    with open(args.path, "r") as file:
        try:
            rules, facts, queries = parse(file.read())
            trees = resolve(rules, facts, queries)
            print_trees(trees, args.visual)
            if args.interactive:
                q = input("Enter your query (or 'exit' to quit): ")
                while q != 'exit':
                    try:
                        nfacts, nqueries = parse_user_input(q)
                        trees = resolve(rules, nfacts if nfacts else facts, nqueries if nqueries else queries)
                        print_trees(trees, args.visual)
                    except SyntaxError as se:
                        print(f"Syntax Error: {se}")
                    except Exception as e:
                        print(f"Error: {e}")
                    q = input("Enter your query (or 'exit' to quit): ")

        except SyntaxError as se:
                print(f"Syntax Error: {se}")
        except Exception as e:
            raise e
            print(f"Error: {e}")
        except KeyboardInterrupt:
            pass