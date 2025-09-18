import collections
import networkx as nx


def delete_pair(man, woman, men_prefs, women_prefs):
    """
    Permanently removes the man-woman pair from each other's preference lists.
    """
    # Remove woman from man's preference list
    for group in list(
        men_prefs.get(man, [])
    ):  # Make a copy to avoid modification during iteration
        if woman in group:
            group.remove(woman)
            # If group is now empty, remove it from the list
            if not group:
                men_prefs[man].remove(group)
            break
    # Remove man from woman's preference list
    for group in list(
        women_prefs.get(woman, [])
    ):  # Make a copy to avoid modification during iteration
        if man in group:
            group.remove(man)
            # If group is now empty, remove it from the list
            if not group:
                women_prefs[woman].remove(group)
            break


def find_critical_set(G_engagements, mcm, all_men):
    """
    Finds the critical set Z. This version uses a corrected alternating path search
    that operates consistently on the graph of engagements.
    """

    # Find the MCM within the engagement graph
    mcm.update({v: k for k, v in mcm.items()})

    # ## Step 2: Find All Reachable Men via Alternating Paths ##

    unmatched_men_U = {m for m in all_men if m not in mcm}

    # The search for alternating paths starts from the unmatched men
    q = collections.deque([(man, "man_step") for man in unmatched_men_U])
    visited = set(unmatched_men_U)
    reachable_men_R = set()

    while q:
        current_node, step_type = q.popleft()

        if step_type == "man_step":
            # A man traverses a NON-MATCHING edge to a woman.
            # The universe of possible edges is the engagement graph itself.
            search_space = G_engagements.neighbors(current_node)

            for woman in search_space:
                # An edge is non-matching if it's in G_engagements but not the MCM
                if mcm.get(current_node) != woman and woman not in visited:
                    visited.add(woman)
                    q.append((woman, "woman_step"))

        elif step_type == "woman_step":
            # A woman must traverse a MATCHING edge to a man
            if current_node in mcm:
                man = mcm[current_node]
                if man not in visited:
                    visited.add(man)
                    reachable_men_R.add(man)
                    q.append((man, "man_step"))

    return unmatched_men_U.union(reachable_men_R)


def super_stable_matching(men_prefs_orig, women_prefs_orig):
    """
    Implements the specific iterative algorithm provided by the user to find
    a super-stable matching. This version correctly handles the dynamic proposal phase.
    """
    # --- INITIALIZATION ---
    men = list(men_prefs_orig.keys())
    women = list(women_prefs_orig.keys())
    men_prefs = {m: [list(g) for g in prefs] for m, prefs in men_prefs_orig.items()}
    women_prefs = {w: [list(g) for g in prefs] for w, prefs in women_prefs_orig.items()}
    women_rank_map = {
        w: {m: i for i, group in enumerate(prefs) for m in group}
        for w, prefs in women_prefs_orig.items()
    }
    engagements = collections.defaultdict(list)
    # 'repeat ... until' loop
    while True:
        # Determine the set of men who are free at the start of this entire round
        initial_free_men = [
            m
            for m in men
            if not any(m in engaged_men for engaged_men in engagements.values())
        ]
        free_men_queue = collections.deque(initial_free_men)

        # --- DYNAMIC PROPOSAL PHASE ---
        # This 'while' loop now correctly continues until no men are free.
        while free_men_queue:
            m = free_men_queue.popleft()
            men_prefs[m] = [group for group in men_prefs[m] if group]
            if not men_prefs[m]:
                continue
            head_of_list = men_prefs[m][0]
            for w in head_of_list:
                if m not in engagements[w]:
                    engagements[w].append(m)

                m_rank_on_w_list = women_rank_map[w][m]

                for group in list(women_prefs[w]):
                    for m_prime in list(group):
                        if women_rank_map[w].get(m_prime, -1) > m_rank_on_w_list:
                            was_engaged = m_prime in engagements.get(w, [])
                            if was_engaged:
                                engagements[w].remove(m_prime)

                                # Check if m_prime is now not engaged to any other women
                                is_now_fully_free = not any(
                                    m_prime in v for v in engagements.values()
                                )
                                if is_now_fully_free:
                                    free_men_queue.append(
                                        m_prime
                                    )  # Add him back to the queue

                            delete_pair(m_prime, w, men_prefs, women_prefs)

        # --- CONFLICT RESOLUTION PHASE ---
        # This phase runs only AFTER the proposal phase has fully completed.
        multiply_engaged_women = [w for w, men in engagements.items() if len(men) > 1]
        for w in multiply_engaged_women:
            engagements[w] = []
            women_prefs[w] = [group for group in women_prefs[w] if group]
            if not women_prefs[w]:
                continue

            tail_of_list = women_prefs[w][-1]
            for m_tail in list(tail_of_list):
                delete_pair(m_tail, w, men_prefs, women_prefs)

        # --- TERMINATION CHECK ---
        currently_free_men = [
            m for m in men if not any(m in v for v in engagements.values())
        ]
        if any(not men_prefs[m] for m in currently_free_men):
            print("No super-stable matching exists (a free man has an empty list).")
            return None

        is_perfect_matching = len(engagements) == len(men) and all(
            len(v) == 1 for v in engagements.values()
        )
        if is_perfect_matching:
            print("Found a super-stable matching!")
            final_matching = {w: men[0] for w, men in engagements.items()}
            return final_matching


def strongly_stable_matching(men_prefs_orig, women_prefs_orig):
    """
    Implements the complete iterative algorithm to find a strongly stable matching.
    """
    # --- Initialization ---
    all_men = list(men_prefs_orig.keys())
    all_women = list(women_prefs_orig.keys())
    if len(all_men) != len(all_women):
        print("Algorithm requires an equal number of men and women.")
        return None

    men_prefs = {m: [list(g) for g in prefs] for m, prefs in men_prefs_orig.items()}
    women_prefs = {w: [list(g) for g in prefs] for w, prefs in women_prefs_orig.items()}
    women_rank_map = {
        w: {m: i for i, group in enumerate(prefs) for m in group}
        for w, prefs in women_prefs_orig.items()
    }
    engagements = collections.defaultdict(list)

    # --- Main 'repeat...until' Loop ---
    max_iterations = len(all_men) ** 2  # Safety break to prevent true infinite loops
    for _ in range(max_iterations):

        # 1. --- PROPOSAL PHASE ---
        free_men_queue = collections.deque(
            [m for m in all_men if not any(m in v for v in engagements.values())]
        )
        while free_men_queue:
            m = free_men_queue.popleft()
            if not men_prefs[m]:
                # Men with empty preference lists cannot propose
                continue
            for w in men_prefs[m][0]:
                if m not in engagements[w]:
                    engagements[w].append(m)
                m_rank = women_rank_map.get(w, {}).get(m)

                for group in list(women_prefs.get(w, [])):
                    for m_prime in list(group):
                        if women_rank_map.get(w, {}).get(m_prime, -1) > m_rank:
                            if m_prime in engagements.get(w, []):
                                engagements[w].remove(m_prime)
                                if not any(m_prime in v for v in engagements.values()):
                                    free_men_queue.append(m_prime)
                            delete_pair(m_prime, w, men_prefs, women_prefs)
        print(engagements)
        # 2. --- CONFLICT RESOLUTION PHASE ---
        engagements_graph = create_bipartite_graph(all_men, all_women, engagements)
        mcm = nx.bipartite.maximum_matching(engagements_graph, top_nodes=set(all_men))
        # A perfect matching is where every man is matched in the maximum cardinality matching        men_matches = {k: v for k, v in mcm.items() if k in all_men}
        men_matches = {k: v for k, v in mcm.items() if k in all_men}

        is_perfect_matching = len(men_matches) == len(all_men)

        if not is_perfect_matching:
            # Find the critical set Z
            critical_set_z = find_critical_set(engagements_graph, mcm, all_men)

            # Find each woman who is engaged to at least one man in Z
            women_to_reset = set()
            for w, suitors in engagements.items():
                if any(man in critical_set_z for man in suitors):
                    women_to_reset.add(w)

            # Break each engagement for these women and delete all pairs at the bottom of her list
            for w in women_to_reset:
                for m in engagements[w]:
                    free_men_queue.append(m)
                engagements[w] = []
                women_prefs[w] = [g for g in women_prefs[w] if g]
                if not women_prefs[w]:
                    continue
                tail_men = women_prefs[w][-1]
                for m_tail in list(
                    tail_men
                ):  # Make a copy to avoid modification during iteration
                    delete_pair(m_tail, w, men_prefs, women_prefs)

        # 3. --- TERMINATION CHECK ---
        if is_perfect_matching:
            print("Successfully found a strongly stable matching.")
            # Return the actual maximum cardinality matching (only women->men pairs)
            final_matching = {w: m for m, w in mcm.items() if m in all_men}
            return final_matching

        currently_free_men = [
            m for m in all_men if not any(m in v for v in engagements.values())
        ]
        if any(not men_prefs[m] for m in currently_free_men):
            print("Remaining men_prefs:", men_prefs)
            print("No strongly stable matching exists.")
            print("Completed iterations:", _ + 1)
            return None

    print("Algorithm failed to converge within the maximum number of iterations.")
    return None


def create_bipartite_graph(all_men, all_women, engagements):
    """
    Creates a bipartite graph from the current engagements.
    """
    men_set, women_set = set(all_men), set(all_women)

    # ## Step 1: Find the Maximum Cardinality Matching ##

    # Build a graph representing ONLY the current engagements
    G_engagements = nx.Graph()
    G_engagements.add_nodes_from(men_set, bipartite=0)
    G_engagements.add_nodes_from(women_set, bipartite=1)
    for woman, men_list in engagements.items():
        for man in men_list:
            G_engagements.add_edge(man, woman)
    return G_engagements
