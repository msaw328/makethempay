-- Database generated with pgModeler (PostgreSQL Database Modeler).
-- pgModeler  version: 0.9.3-beta1
-- PostgreSQL version: 13.0
-- Project Site: pgmodeler.io
-- Model Author: ---

-- Database creation must be performed outside a multi lined SQL file. 
-- These commands were put in this file only as a convenience.
-- 
-- object: makethempay | type: DATABASE --
DROP DATABASE IF EXISTS makethempay;
CREATE DATABASE makethempay;
-- ddl-end --

\c makethempay;

SET check_function_bodies = false;
-- ddl-end --

-- object: public.users | type: TABLE --
DROP TABLE IF EXISTS public.users CASCADE;
CREATE TABLE public.users (
	id serial NOT NULL,
	email_addr varchar(300) NOT NULL,
	password_hash varchar(80) NOT NULL,
	CONSTRAINT user_id PRIMARY KEY (id),
	CONSTRAINT email_unique UNIQUE (email_addr),
	CONSTRAINT password_hash_unique UNIQUE (password_hash)

);
-- ddl-end --
COMMENT ON COLUMN public.users.email_addr IS E'used as login';
-- ddl-end --
COMMENT ON COLUMN public.users.password_hash IS E'probably argon2';
-- ddl-end --
ALTER TABLE public.users OWNER TO postgres;
-- ddl-end --

-- object: public.groups | type: TABLE --
DROP TABLE IF EXISTS public.groups CASCADE;
CREATE TABLE public.groups (
	id serial NOT NULL,
	display_name varchar(63) NOT NULL,
	access_token varchar(31) NOT NULL,
	description text,
	CONSTRAINT group_id PRIMARY KEY (id),
	CONSTRAINT access_token_unique UNIQUE (access_token)

);
-- ddl-end --
COMMENT ON COLUMN public.groups.access_token IS E'random token used to join a group';
-- ddl-end --
COMMENT ON CONSTRAINT access_token_unique ON public.groups  IS E'access token has to identify the group';
-- ddl-end --
ALTER TABLE public.groups OWNER TO postgres;
-- ddl-end --

-- object: public.memberships | type: TABLE --
DROP TABLE IF EXISTS public.memberships CASCADE;
CREATE TABLE public.memberships (
	id serial NOT NULL,
	user_id integer NOT NULL,
	group_id integer NOT NULL,
	user_display_name varchar(63) NOT NULL,
	status varchar(127),
	CONSTRAINT users_in_groups_id PRIMARY KEY (id),
	CONSTRAINT user_unique_in_group UNIQUE (user_id,group_id),
	CONSTRAINT user_display_name_unique_in_group UNIQUE (group_id,user_display_name)

);
-- ddl-end --
COMMENT ON TABLE public.memberships IS E'describes membership of a user in a group';
-- ddl-end --
ALTER TABLE public.memberships OWNER TO postgres;
-- ddl-end --

-- object: public.expenses | type: TABLE --
DROP TABLE IF EXISTS public.expenses CASCADE;
CREATE TABLE public.expenses (
	id serial NOT NULL,
	creditor_id integer NOT NULL,
	name varchar(63) NOT NULL,
	description text,
	CONSTRAINT expense_id PRIMARY KEY (id)

);
-- ddl-end --
COMMENT ON TABLE public.expenses IS E'a row in this table describes an expense made as a group';
-- ddl-end --
COMMENT ON COLUMN public.expenses.creditor_id IS E'the person who PAID and others owe THEM money';
-- ddl-end --
ALTER TABLE public.expenses OWNER TO postgres;
-- ddl-end --

-- object: public.debts | type: TABLE --
DROP TABLE IF EXISTS public.debts CASCADE;
CREATE TABLE public.debts (
	id serial NOT NULL,
	expense_id integer NOT NULL,
	debtor_id integer NOT NULL,
	amount_paid money NOT NULL,
	amount_owed money NOT NULL,
	CONSTRAINT debtor_id PRIMARY KEY (id),
	CONSTRAINT debtor_only_once_in_expense UNIQUE (debtor_id,expense_id),
	CONSTRAINT paid_not_greater_than_owed CHECK (amount_paid <= amount_owed)

);
-- ddl-end --
COMMENT ON COLUMN public.debts.debtor_id IS E'who owes the money';
-- ddl-end --
COMMENT ON CONSTRAINT debtor_only_once_in_expense ON public.debts  IS E'check if debtor is present only once in any expense';
-- ddl-end --
ALTER TABLE public.debts OWNER TO postgres;
-- ddl-end --

-- object: public.tf_debtor_id_check | type: FUNCTION --
DROP FUNCTION IF EXISTS public.tf_debtor_id_check() CASCADE;
CREATE FUNCTION public.tf_debtor_id_check ()
	RETURNS trigger
	LANGUAGE plpgsql
	VOLATILE 
	CALLED ON NULL INPUT
	SECURITY INVOKER
	COST 1
	AS $$
declare
	debtor_group_id integer := (select memberships.group_id from memberships where memberships.id = NEW.debtor_id);
	creditor_id integer := (select expenses.creditor_id from expenses where expenses.id = NEW.expense_id);
	creditor_group_id integer := (select memberships.group_id from memberships where memberships.id = creditor_id);

begin
	if debtor_group_id <> creditor_group_id then
		raise notice 'Debtor (id %/grp id %) must be in the same group as creditor (id %/grp id %)!', NEW.debtor_id, debtor_group_id, creditor_id, creditor_group_id;
		return null;
	end if;

	if creditor_id = NEW.debtor_id then
		raise notice 'Debtor (id %) must be a different person than the creditor (id %)!', NEW.debtor_id, creditor_id;
		return null;
	end if;

	return NEW;
end;

$$;
-- ddl-end --
ALTER FUNCTION public.tf_debtor_id_check() OWNER TO postgres;
-- ddl-end --
COMMENT ON FUNCTION public.tf_debtor_id_check() IS E'checks if debtor is in the same group as creditor of the expense, or if the debtor and creditor is the same person';
-- ddl-end --

-- object: t_debtor_id_checks | type: TRIGGER --
DROP TRIGGER IF EXISTS t_debtor_id_checks ON public.debts CASCADE;
CREATE TRIGGER t_debtor_id_checks
	BEFORE INSERT OR UPDATE
	ON public.debts
	FOR EACH ROW
	EXECUTE PROCEDURE public.tf_debtor_id_check('');
-- ddl-end --

-- object: user_id_in_users | type: CONSTRAINT --
-- ALTER TABLE public.memberships DROP CONSTRAINT IF EXISTS user_id_in_users CASCADE;
ALTER TABLE public.memberships ADD CONSTRAINT user_id_in_users FOREIGN KEY (user_id)
REFERENCES public.users (id) MATCH FULL
ON DELETE CASCADE ON UPDATE CASCADE;
-- ddl-end --

-- object: group_id_in_groups | type: CONSTRAINT --
-- ALTER TABLE public.memberships DROP CONSTRAINT IF EXISTS group_id_in_groups CASCADE;
ALTER TABLE public.memberships ADD CONSTRAINT group_id_in_groups FOREIGN KEY (group_id)
REFERENCES public.groups (id) MATCH FULL
ON DELETE CASCADE ON UPDATE CASCADE;
-- ddl-end --

-- object: creditor_in_memberships_id | type: CONSTRAINT --
-- ALTER TABLE public.expenses DROP CONSTRAINT IF EXISTS creditor_in_memberships_id CASCADE;
ALTER TABLE public.expenses ADD CONSTRAINT creditor_in_memberships_id FOREIGN KEY (creditor_id)
REFERENCES public.memberships (id) MATCH FULL
ON DELETE CASCADE ON UPDATE CASCADE;
-- ddl-end --

-- object: expense_id_in_expenses | type: CONSTRAINT --
-- ALTER TABLE public.debts DROP CONSTRAINT IF EXISTS expense_id_in_expenses CASCADE;
ALTER TABLE public.debts ADD CONSTRAINT expense_id_in_expenses FOREIGN KEY (expense_id)
REFERENCES public.expenses (id) MATCH FULL
ON DELETE CASCADE ON UPDATE CASCADE;
-- ddl-end --

-- object: debtor_id_in_memberships | type: CONSTRAINT --
-- ALTER TABLE public.debts DROP CONSTRAINT IF EXISTS debtor_id_in_memberships CASCADE;
ALTER TABLE public.debts ADD CONSTRAINT debtor_id_in_memberships FOREIGN KEY (debtor_id)
REFERENCES public.memberships (id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --


