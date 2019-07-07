# Variables

There are several variables that are valid for all roles doeses project.

## Proxy Setttings

We used for internet access a proy this can be deposited in the following variable.

```yml
default_proxy:
default_proxy_password:
default_proxy_username:
default_validate_certs:
```

## Windows Group Policie

The Windows roles use policy settings of the GPO of Windows. For conflict avoidance the value can be set to Fales.

```yml
default_GPO_enable:
```
