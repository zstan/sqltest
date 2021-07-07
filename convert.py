import json

def generate_tc(path):
    out_xml = open('out_tc.xml', 'w')
    tc_template = ""

    with open('tc_template.xml', 'r') as f:
        tc_template = f.read()

    with open(path, 'r') as f:
        input = f.read().replace('\n', '')

        data = json.loads(input)
        total = 0
        passed = 0
        test_case = []
        for case in ('mandatory', 'optional'):
            for test in data['features'][case]:
                body = data['features'][case][test]
                total0 = body['total']
                passed0 = body['pass']
                total += total0
                passed += passed0
                test_case.append({'name': test + " " + body['description'], 'classname': test + " " + case,
                                  'errors': total0 - passed0, 'total': total0})

        tc_template = tc_template.replace('%total%', str(total))
        tc_template = tc_template.replace('%failed%', str(total - passed))
        print ("total: ", total)
        print ("failed: ", total - passed)

        test_cases = ""
        for t in test_case:
            complete = ' />\n\n' if t['errors'] == 0 else '>'
            test_cases += "<testcase classname=\"" + t['classname'] + "\" name=\"" + t['name'] + "\"" + complete
            if t['errors'] != 0:
                test_cases += "<failure message=\"failed " + str(t['errors']) + " from " + str(t['total']) + " tests\" " \
                    "type=\"" + test + "\"></failure></testcase>\n\n"

        tc_template = tc_template.replace('%testcase%', test_cases)

                #out_xml.write(json2xml.Json2xml(data).to_xml())
        out_xml.write(tc_template)

    out_xml.close()

if __name__ == '__main__':
    generate_tc()
