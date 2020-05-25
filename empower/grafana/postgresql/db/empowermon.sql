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

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: bin_stats; Type: TABLE; Schema: public; Owner: empower
--

CREATE TABLE public.bin_stats (
    id integer NOT NULL,
    lvap_addr text,
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
-- Name: lvap_association_stats; Type: TABLE; Schema: public; Owner: empower
--

CREATE TABLE public.lvap_association_stats (
    id integer NOT NULL,
    lvap_addr text,
    wtp_addr text,
    flag integer,
    timestamp_ms bigint
);


ALTER TABLE public.lvap_association_stats OWNER TO empower;

--
-- Name: lvap_association_stats_id_seq; Type: SEQUENCE; Schema: public; Owner: empower
--

CREATE SEQUENCE public.lvap_association_stats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lvap_association_stats_id_seq OWNER TO empower;

--
-- Name: lvap_association_stats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: empower
--

ALTER SEQUENCE public.lvap_association_stats_id_seq OWNED BY public.lvap_association_stats.id;


--
-- Name: lvap_stats; Type: TABLE; Schema: public; Owner: empower
--

CREATE TABLE public.lvap_stats (
    id integer NOT NULL,
    lvap_addr text,
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
-- Name: mcda_association_stats; Type: TABLE; Schema: public; Owner: empower
--

CREATE TABLE public.mcda_association_stats (
    id integer NOT NULL,
    lvap_addr text,
    wtp_addr text,
    association_flag integer,
    timestamp_ms bigint
);


ALTER TABLE public.mcda_association_stats OWNER TO empower;

--
-- Name: mcda_association_id_seq; Type: SEQUENCE; Schema: public; Owner: empower
--

CREATE SEQUENCE public.mcda_association_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mcda_association_id_seq OWNER TO empower;

--
-- Name: mcda_association_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: empower
--

ALTER SEQUENCE public.mcda_association_id_seq OWNED BY public.mcda_association_stats.id;


--
-- Name: mcda_results; Type: TABLE; Schema: public; Owner: empower
--

CREATE TABLE public.mcda_results (
    id integer NOT NULL,
    lvap_addr text,
    wtp_addr text,
    wtp_channel_load_rate double precision,
    wtp_sta_rssi_dbm double precision,
    wtp_load_expected_mbps double precision,
    wtp_load_measured_mbps double precision,
    wtp_queue_delay_ms double precision,
    sta_association_flag integer,
    rank integer,
    closeness double precision,
    timestamp_ms bigint
);


ALTER TABLE public.mcda_results OWNER TO empower;

--
-- Name: mcda_results_id_seq; Type: SEQUENCE; Schema: public; Owner: empower
--

CREATE SEQUENCE public.mcda_results_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mcda_results_id_seq OWNER TO empower;

--
-- Name: mcda_results_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: empower
--

ALTER SEQUENCE public.mcda_results_id_seq OWNED BY public.mcda_results.id;


--
-- Name: mcda_weights; Type: TABLE; Schema: public; Owner: empower
--

CREATE TABLE public.mcda_weights (
    id integer NOT NULL,
    wtp_channel_load_rate double precision,
    wtp_sta_rssi_dbm double precision,
    wtp_load_expected_mbps double precision,
    wtp_load_measured_mbps double precision,
    wtp_queue_delay_ms double precision,
    sta_association_flag double precision,
    timestamp_ms bigint,
    type text
);


ALTER TABLE public.mcda_weights OWNER TO empower;

--
-- Name: mcda_weights_id_seq; Type: SEQUENCE; Schema: public; Owner: empower
--

CREATE SEQUENCE public.mcda_weights_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mcda_weights_id_seq OWNER TO empower;

--
-- Name: mcda_weights_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: empower
--

ALTER SEQUENCE public.mcda_weights_id_seq OWNED BY public.mcda_weights.id;


--
-- Name: ncqm_stats; Type: TABLE; Schema: public; Owner: empower
--

CREATE TABLE public.ncqm_stats (
    id integer NOT NULL,
    wtp_addr text,
    hist_packets bigint,
    last_packets bigint,
    last_rssi_avg integer,
    last_rssi_std integer,
    mov_rssi integer,
    timestamp_ms bigint,
    unknown_ap_addr text
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
-- Name: slice_stats; Type: TABLE; Schema: public; Owner: empower
--

CREATE TABLE public.slice_stats (
    id integer NOT NULL,
    wtp_addr text,
    dscp text,
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
    wtp_dscp text,
    crr_queue_length bigint
);


ALTER TABLE public.slice_stats OWNER TO empower;

--
-- Name: slice_stats_id_seq; Type: SEQUENCE; Schema: public; Owner: empower
--

CREATE SEQUENCE public.slice_stats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.slice_stats_id_seq OWNER TO empower;

--
-- Name: slice_stats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: empower
--

ALTER SEQUENCE public.slice_stats_id_seq OWNED BY public.slice_stats.id;


--
-- Name: ucqm_stats; Type: TABLE; Schema: public; Owner: empower
--

CREATE TABLE public.ucqm_stats (
    id integer NOT NULL,
    wtp_addr text,
    hist_packets bigint,
    last_packets bigint,
    last_rssi_avg integer,
    last_rssi_std integer,
    mov_rssi integer,
    timestamp_ms bigint,
    wtp_sta text,
    sta_addr text
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
-- Name: wifi_stats; Type: TABLE; Schema: public; Owner: empower
--

CREATE TABLE public.wifi_stats (
    id integer NOT NULL,
    tx double precision,
    rx double precision,
    channel_utilization double precision,
    timestamp_ms bigint,
    wtp_addr text,
    channel integer
);


ALTER TABLE public.wifi_stats OWNER TO empower;

--
-- Name: wifi_stats_id_seq; Type: SEQUENCE; Schema: public; Owner: empower
--

CREATE SEQUENCE public.wifi_stats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.wifi_stats_id_seq OWNER TO empower;

--
-- Name: wifi_stats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: empower
--

ALTER SEQUENCE public.wifi_stats_id_seq OWNED BY public.wifi_stats.id;


--
-- Name: bin_stats id; Type: DEFAULT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.bin_stats ALTER COLUMN id SET DEFAULT nextval('public.bin_stats_id_seq'::regclass);


--
-- Name: lvap_association_stats id; Type: DEFAULT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.lvap_association_stats ALTER COLUMN id SET DEFAULT nextval('public.lvap_association_stats_id_seq'::regclass);


--
-- Name: lvap_stats id; Type: DEFAULT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.lvap_stats ALTER COLUMN id SET DEFAULT nextval('public.lvap_stats_id_seq'::regclass);


--
-- Name: mcda_association_stats id; Type: DEFAULT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.mcda_association_stats ALTER COLUMN id SET DEFAULT nextval('public.mcda_association_id_seq'::regclass);


--
-- Name: mcda_results id; Type: DEFAULT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.mcda_results ALTER COLUMN id SET DEFAULT nextval('public.mcda_results_id_seq'::regclass);


--
-- Name: mcda_weights id; Type: DEFAULT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.mcda_weights ALTER COLUMN id SET DEFAULT nextval('public.mcda_weights_id_seq'::regclass);


--
-- Name: ncqm_stats id; Type: DEFAULT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.ncqm_stats ALTER COLUMN id SET DEFAULT nextval('public.ncqm_stats_id_seq'::regclass);


--
-- Name: slice_stats id; Type: DEFAULT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.slice_stats ALTER COLUMN id SET DEFAULT nextval('public.slice_stats_id_seq'::regclass);


--
-- Name: ucqm_stats id; Type: DEFAULT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.ucqm_stats ALTER COLUMN id SET DEFAULT nextval('public.ucqm_stats_id_seq'::regclass);


--
-- Name: wifi_stats id; Type: DEFAULT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.wifi_stats ALTER COLUMN id SET DEFAULT nextval('public.wifi_stats_id_seq'::regclass);


--
-- Name: bin_stats bin_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.bin_stats
    ADD CONSTRAINT bin_stats_pkey PRIMARY KEY (id);


--
-- Name: lvap_association_stats lvap_association_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.lvap_association_stats
    ADD CONSTRAINT lvap_association_stats_pkey PRIMARY KEY (id);


--
-- Name: lvap_stats lvap_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.lvap_stats
    ADD CONSTRAINT lvap_stats_pkey PRIMARY KEY (id);


--
-- Name: mcda_association_stats mcda_association_pkey; Type: CONSTRAINT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.mcda_association_stats
    ADD CONSTRAINT mcda_association_pkey PRIMARY KEY (id);


--
-- Name: mcda_results mcda_results_pkey; Type: CONSTRAINT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.mcda_results
    ADD CONSTRAINT mcda_results_pkey PRIMARY KEY (id);


--
-- Name: mcda_weights mcda_weights_pkey; Type: CONSTRAINT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.mcda_weights
    ADD CONSTRAINT mcda_weights_pkey PRIMARY KEY (id);


--
-- Name: ncqm_stats ncqm_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.ncqm_stats
    ADD CONSTRAINT ncqm_stats_pkey PRIMARY KEY (id);


--
-- Name: slice_stats slice_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.slice_stats
    ADD CONSTRAINT slice_stats_pkey PRIMARY KEY (id);


--
-- Name: ucqm_stats ucqm_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.ucqm_stats
    ADD CONSTRAINT ucqm_stats_pkey PRIMARY KEY (id);


--
-- Name: wifi_stats wifi_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: empower
--

ALTER TABLE ONLY public.wifi_stats
    ADD CONSTRAINT wifi_stats_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

