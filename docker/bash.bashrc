export TERM=xterm-256color
alias grep="grep --color=auto"
alias ls="ls --color=auto"

echo -e "\e[1;31m"
cat<<TF
-----------------------------------------------------------------------
##### #     ##### #   # ##### ##### ##### ##### ##### ##### ##### #   #
#     #     #     #   # #     #   # #     #   # #     #     #     #   #
#     #     #     #   # #     #   # #     #   # #     #     #     #   #
#     #     ###   #   # ###   ##### ##### ##### ###   ###   #     #####
#     #     #      # #  #     # #       # #     #     #     #     #   #
#     #     #      # #  #     #  #      # #     #     #     #     #   #
##### ##### #####   #   ##### #   # ##### #     ##### ##### ##### #   #
-----------------------------------------------------------------------
TF
echo -e "\e[0;33m"

if [[ $EUID -eq 0 ]]; then
  cat <<WARNROOT
-----------------------------------------------------------------------
===> WARNING: container user is root
-----------------------------------------------------------------------
WARNROOT
elif [[ $EUID -eq 9999 && $(id -g) -eq 9999 ]]; then
  cat <<WARN
-----------------------------------------------------------------------
===> WARNING: container user is cleverspeech
-----------------------------------------------------------------------
You are running this container as the base container user with:

  ID    $(id -u)
  GROUP $(id -g)

This will not map to the user on your docker host so you will need to
chown any results data.
-----------------------------------------------------------------------
WARN
else
  cat <<OKAY
-----------------------------------------------------------------------
You are running this container as a user with

  ID    $(id -u)
  GROUP $(id -g)

This is different to the base container user (and is not root).
I should have chown-ed important data files so you can use them.
-----------------------------------------------------------------------
OKAY
fi
# Turn off colors
echo -e "\e[m"
