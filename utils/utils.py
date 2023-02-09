




def get_url(arxiv_id):
    # Get url from arxiv_id
    # Id should be in YYMM.NNNNN format but sometimes it's not
    # so we have to add a leading 0 if necessary
    arxiv_id = str(arxiv_id)
    first_part = arxiv_id.split(".")[0]
    second_part = arxiv_id.split(".")[1]

    if len(first_part) != 4:
        while len(first_part) < 4:
            first_part = "0" + first_part
    
    if len(second_part) != 5:
        while len(second_part) < 5:
            second_part = "0" + second_part
    
    return "https://arxiv.org/abs/" + first_part + "." + second_part
