from rules.predicates import predicate


@predicate
def is_adult_cat(user, cat=None):
    if cat is None:
        return True

    return cat.age >= 3
