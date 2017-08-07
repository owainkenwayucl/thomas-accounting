# Thomas accounting tools

BEFORE USING THESE TOOLS SERIOUSLY CONSIDER HOW YOUR LIFE HAS COME TO THIS POINT AND COME AND TALK TO ME ABOUT IT PLEASE.

Regardless, these are MIT licensed.

These tools a temporary kludge until we move to SAFE.  If it's 2018 and you are still using them something has gone very wrong.

These tools only work on Thomas.

They only work if you have also installed my `fpsum` utility into your `$PATH` from here: https://github.com/owainkenwayucl/utils

They only work if you've put the very secret DB config file in the right place.

Current tools:

 * `get-accounting <year> <month>` - this looks at the Gold database to get the amount of credits spent in a particular month, and then at the `thomas_sgelogs` database to get the number of CPU hours used in that month and then combines the two to work out the % of usage that was paid (high priority) vs. free.

 * `get-institutional-accounting <year> <month>` - this looks at the `thomas` database to get a list of users at each institute, at the Gold database to get the amount of credits spent by that institute in a particular month, and then at the `thomas_sgelogs` database to get the number of CPU hours used by those users in that month and then combines the two to work out the % of usage that was paid (high priority) vs. free.  It's incorrect where a user is at more than one institute.

##TODO: Basically everything.
