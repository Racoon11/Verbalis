def jacquard(pu, pv):
    su, sv = set(pu), set(pv)
    return 1 - len(su & sv) / len(su | sv)
