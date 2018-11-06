from pmlab_lite.log import *

def print_log(l):
    for t in l.get_traces():
        print("TRACE:")
        for e in t:
            print(">", e.get_activity_name(), e.get_case_id(), e.get_attributes())


if __name__ == "__main__":
    l = EventLog()
    l.add_event(Event("A", 1))
    l.add_event(Event("D", 2)).add_event(Event("C", 1))
    l.add_event(Event("E", 2)).add_event(Event("B", 1)).add_event(Event("F", 2))
    l.add_trace(3, ["A", "B", "C"])

    print("=== LOG ===")
    print_log(l)

    print("\n=== FILTERING (projecting only A) ===")
    print_log(l.ProjectActivities("A"))

    print("\n=== FILTERING (projecting only E, F, K) ===")
    print_log(l.ProjectActivities(["E", "F", "K"]))

    print("\n=== FILTERING (projecting only attribute case_id = 1) ===")
    print_log(l.FilterPerAttribute("case_id", 1))

    print("\n=== FILTERING (projecting only attribute case_id = 2 or case_id = 3) ===")
    print_log(l.FilterPerAttribute("case_id", [3, 2]))

    print("\n=== FILTERING (traces starting with A) ===")
    print_log(l.TracesStartingWith("A"))

    print("\n=== FILTERING (traces ending with F) ===")
    print_log(l.TracesEndingWith("F"))

    print("\n=== FILTERING (traces with direct following relationship B -> C) ===")
    print_log(l.TracesWithDirectFollowing("B", "C"))