--
-- PostgreSQL database dump
--

-- Dumped from database version 10.12 (Ubuntu 10.12-0ubuntu0.18.04.1)
-- Dumped by pg_dump version 10.12 (Ubuntu 10.12-0ubuntu0.18.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: bin_stats; Type: TABLE; Schema: public; Owner: empower
--

CREATE TABLE public.bin_stats (
    id integer NOT NULL,
    lvap text,
    rx_bytes bigint,
    rx_bytes_per_second double precision,
    rx_packets bigint,
    rx_packets_per_second double precision,
    tx_bytes bigint,
    tx_bytes_per_second double precision,
    tx_packets_per_second double precision,
    tx_packets bigint,
    timestamp_ms bigint,
    tx_throughput_mbps double precision,
    rx_throughput_mbps double precision
);


ALTER TABLE public.bin_stats OWNER TO empower;

--
-- Name: bin_stats_id_seq; Type: SEQUENCE; Schema: public; Owner: empower
--

CREATE SEQUENCE public.bin_stats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bin_stats_id_seq OWNER TO empower;

--
-- Name: bin_stats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: empower
--

ALTER SEQUENCE public.bin_stats_id_seq OWNED BY public.bin_stats.id;


--
-- Name: lvap_stats; Type: TABLE; Schema: public; Owner: empower
--

CREATE TABLE public.lvap_stats (
    id integer NOT NULL,
    address text,
    best_mcs_prob integer,
    timestamp_ms bigint
);


ALTER TABLE public.lvap_stats OWNER TO empower;

--
-- Name: lvap_stats_id_seq; Type: SEQUENCE; Schema: public; Owner: empower
--

CREATE SEQUENCE public.lvap_stats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lvap_stats_id_seq OWNER TO empower;

--
-- Name: lvap_stats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: empower
--

ALTER SEQUENCE public.lvap_stats_id_seq OWNED BY public.lvap_stats.id;


--
-- Name: ncqm_stats; Type: TABLE; Schema: public; Owner: empower
--

CREATE TABLE public.ncqm_stats (
    id integer NOT NULL,
    address text,
    hist_packets bigint,
    last_packets bigint,
    last_rssi_avg integer,
    last_rssi_std integer,
    mov_rssi integer,
    timestamp_ms bigint,
    wtp_ap text
);


ALTER TABLE public.ncqm_stats OWNER TO empower;

--
-- Name: ncqm_stats_id_seq; Type: SEQUENCE; Schema: public; Owner: empower
--

CREATE SEQUENCE public.ncqm_stats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ncqm_stats_id_seq OWNER TO empower;

--
-- Name: ncqm_stats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: empower
--

ALTER SEQUENCE public.ncqm_stats_id_seq OWNED BY public.ncqm_stats.id;


--
-- Name: slice_stats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.slice_stats (
    id integer NOT NULL,
    wtp text,
    slice_dscp text,
    deficit bigint,
    deficit_avg bigint,
    max_queue_length bigint,
    queue_delay_msec double precision,
    tx_bytes double precision,
    tx_packets bigint,
    tx_mbits double precision,
    throughput_mbps double precision,
    timestamp_ms bigint,
    deficit_used bigint,
    current_quantum bigint,
    wtp_dscp text
);


ALTER TABLE public.slice_stats OWNER TO postgres;

--
-- Name: slice_stats_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.slice_stats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.slice_stats_id_seq OWNER TO postgres;

--
-- Name: slice_stats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.slice_stats_id_seq OWNED BY public.slice_stats.id;


--
-- Name: ucqm_stats; Type: TABLE; Schema: public; Owner: empower
--

CREATE TABLE public.ucqm_stats (
    id integer NOT NULL,
    address text,
    hist_packets bigint,
    last_packets bigint,
    last_rssi_avg integer,
    last_rssi_std integer,
    mov_rssi integer,
    timestamp_ms bigint,
    wtp_sta text
);


ALTER TABLE public.ucqm_stats OWNER TO empower;

--
-- Name: ucqm_stats_id_seq; Type: SEQUENCE; Schema: public; Owner: empower
--

CREATE SEQUENCE public.ucqm_stats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ucqm_stats_id_seq OWNER TO empower;

--
-- Name: ucqm_stats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: empower
--

ALTER SEQUENCE public.ucqm_stats_id_seq OWNED BY public.ucqm_stats.id;


--
-- Name: bin_stats id; Type: DEFAULT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.bin_stats ALTER COLUMN id SET DEFAULT nextval('public.bin_stats_id_seq'::regclass);


--
-- Name: lvap_stats id; Type: DEFAULT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.lvap_stats ALTER COLUMN id SET DEFAULT nextval('public.lvap_stats_id_seq'::regclass);


--
-- Name: ncqm_stats id; Type: DEFAULT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.ncqm_stats ALTER COLUMN id SET DEFAULT nextval('public.ncqm_stats_id_seq'::regclass);


--
-- Name: slice_stats id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.slice_stats ALTER COLUMN id SET DEFAULT nextval('public.slice_stats_id_seq'::regclass);


--
-- Name: ucqm_stats id; Type: DEFAULT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.ucqm_stats ALTER COLUMN id SET DEFAULT nextval('public.ucqm_stats_id_seq'::regclass);


--
-- Name: bin_stats bin_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.bin_stats
    ADD CONSTRAINT bin_stats_pkey PRIMARY KEY (id);


--
-- Name: lvap_stats lvap_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.lvap_stats
    ADD CONSTRAINT lvap_stats_pkey PRIMARY KEY (id);


--
-- Name: ncqm_stats ncqm_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.ncqm_stats
    ADD CONSTRAINT ncqm_stats_pkey PRIMARY KEY (id);


--
-- Name: slice_stats slice_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.slice_stats
    ADD CONSTRAINT slice_stats_pkey PRIMARY KEY (id);


--
-- Name: ucqm_stats ucqm_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.ucqm_stats
    ADD CONSTRAINT ucqm_stats_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

