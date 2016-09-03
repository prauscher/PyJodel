#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import random
import datetime
import time

def monitor_jodel(client, handle_post, handle_reply):
    current_position = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
    while True:
        try:
            client.set_location(client.location)

            next_position = current_position
            posts = client.get_posts()
            for post in posts:
                updated_at = datetime.datetime.strptime(post["updated_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
                if updated_at > current_position:
                    post_details = client.get_post(post["post_id"])
                    created_at = datetime.datetime.strptime(post_details["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")

                    if created_at > current_position:
                        handle_post(post_details)
                        next_position = max(next_position, created_at)

                    if "children" in post_details:
                        for children in post_details["children"]:
                            created_at = datetime.datetime.strptime(children["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
                            if created_at > current_position:
                                handle_reply(post["post_id"], children)
                                next_position = max(next_position, created_at)
            current_position = next_position
        except Exception as e:
            print("Monitor error: ".format(str(e)))

        # a bit of obfuscation
        time.sleep(random.randint(90,150))
