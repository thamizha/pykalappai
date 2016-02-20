__author__ = 'manikk'


class ScimTableParser:
    start = False
    scim_mappings = {}

    def parse(self, file_name):
        try:
            f = open(file_name, encoding="utf-8")
            for line in f:
                strip = line.strip().encode("utf-8").decode()
                if strip == "BEGIN_TABLE":
                    self.start = True
                    continue

                if self.start and strip != "END_TABLE":
                    mapping = strip.split(" ")
                    self.scim_mappings[mapping[0]] = mapping[-1]

                if strip == "END_TABLE":
                    self.start = False

            f.close()
            return self.scim_mappings
        except:
            return self.scim_mappings
