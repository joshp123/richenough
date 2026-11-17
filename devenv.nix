{ pkgs, ... }:

{
  packages = [
    pkgs.nodejs_24
    pkgs.buf
  ];
}
