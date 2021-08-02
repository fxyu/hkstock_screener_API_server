import myapi.db as db
import myapi.rules as rules
import myapi.operator as operator
import pandas as pd
import json

def main():
    db_result = db.db_get_all_symbol()
    js_results = [None] * 18

    for rules in range(18):
        print("performing rules {} ...".format(rules))

        js_results[rules] = operator.get_check_rule_results_all(
            operator.get_symbol_list_arr(db_result), rules, "20190101" , "20200201", 0, False)

        with open('rules.json', 'w', encoding='utf-8') as f:
            json.dump(js_results, f, ensure_ascii=False, indent=4)

    

if __name__ == '__main__':
    main() 