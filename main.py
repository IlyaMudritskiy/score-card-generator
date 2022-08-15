import os
from src.code_generators import CodeCombiner
from src.params_handler import ParamsCombiner
from src.settings import get_logger

log = get_logger("main.log")

def main():

    path = os.path.dirname(os.path.abspath(__file__))
    log_dir = "log"
    cards_dir = "cards"

    try:
        os.mkdir(log_dir)
    except Exception as e:
        log.warning(e)
        pass

    try:
        os.mkdir(cards_dir)
    except Exception as e:
        log.warning(e)
        pass

    # Prepare for getting full code
    params_combiner = ParamsCombiner()
    full_cards_info = params_combiner.prepare_all_cards()
    code_combiner = CodeCombiner(full_cards_info)

    # Get code for all cards and all systems
    ready_code = code_combiner.get_code_for_all_cards()

    for code in ready_code:
        # Write code to 'score_card'.md file
        with open(f"{path}/{cards_dir}/{code[0]}.md", "w") as f:
            # Header
            f.write(f"# {code[0]}\n\n")
            # OMDM Code
            f.write("## OMDM Code\n")
            f.write("```js\n")
            for line in code[1]["omdm"].code:
                f.write(line)
            f.write("```\n\n")

            # Blaze code
            f.write("## Blaze code\n")
            f.write("```js\n")
            for line in code[1]["blaze"].code:
                f.write(line)
            f.write("```\n\n")

            # Report fields
            f.write("## Report fields\n")
            f.write("```js\n")
            for line in code[1]["report"].code:
                f.write(line)
            f.write("```\n\n")

if __name__ == "__main__":
    main()