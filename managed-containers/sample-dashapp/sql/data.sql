-- sqlfluff:dialect:postgres
--
-- PostgreSQL database dump
--

-- Dumped from database version 12.20
-- Dumped by pg_dump version 17.1 (Debian 17.1-1.pgdg120+1)

-- Started on 2024-11-21 14:44:44 UTC


SET default_tablespace = '';
SET default_table_access_method = heap;

--
-- TOC entry 203 (class 1259 OID 24851)
-- Name: celestial_bodies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.celestial_bodies (
    id integer NOT NULL,
    name character varying(100),
    body_type character varying(50),
    mean_radius_km numeric,
    mass_kg numeric,
    distance_from_sun_km numeric
);


--
-- TOC entry 202 (class 1259 OID 24849)
-- Name: celestial_bodies_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.celestial_bodies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3565 (class 0 OID 0)
-- Dependencies: 202
-- Name: celestial_bodies_id_seq; 
-- Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.celestial_bodies_id_seq
    OWNED BY public.celestial_bodies.id;


--
-- TOC entry 3429 (class 2604 OID 24854)
-- Name: celestial_bodies id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.celestial_bodies ALTER COLUMN id
    SET DEFAULT nextval('public.celestial_bodies_id_seq'::regclass);


--
-- TOC entry 3559 (class 0 OID 24851)
-- Dependencies: 203
-- Data for Name: celestial_bodies; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.celestial_bodies (id, name, body_type, mean_radius_km, mass_kg, distance_from_sun_km) FROM stdin;   -- noqa: PRS
1	Mercury	Planet	2439.7	330110000000000000000000	57909227 
2	Venus	Planet	6051.8	4867500000000000000000000	108209475
3	Earth	Planet	6371.0	5972370000000000000000000	149598262
4	Mars	Planet	3389.5	641710000000000000000000	227943824
5	Jupiter	Planet	69911	1898200000000000000000000000	778340821
6	Europa	Moon	1560.8	47998000000000000000000	670900000
7	Ganymede	Moon	2634.1	148190000000000000000000	670900000
8	Ceres	Dwarf Planet	473	938350000000000000000	413700000
9	Pluto	Dwarf Planet	1188.3	13030000000000000000000	5906440628
\.


--
-- TOC entry 3566 (class 0 OID 0)
-- Dependencies: 202
-- Name: celestial_bodies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.celestial_bodies_id_seq', 20, true);


--
-- TOC entry 3431 (class 2606 OID 24859)
-- Name: celestial_bodies celestial_bodies_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.celestial_bodies
    ADD CONSTRAINT celestial_bodies_pkey PRIMARY KEY (id);


-- Completed on 2024-11-21 14:44:46 UTC

--
-- PostgreSQL database dump complete
--
